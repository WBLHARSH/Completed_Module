# -*- coding: utf-8 -*-
#
#################################################################################
# Author      : Weblytic Labs Pvt. Ltd. (<https://store.weblyticlabs.com/>)
# Copyright(c): 2023-Present Weblytic Labs Pvt. Ltd.
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
##################################################################################

from odoo import http
from odoo.http import request
import re


class MarketplaceSeller(http.Controller):

    @http.route('/seller/marketing', auth='public', website=True)
    def seller_marketing(self):
        settings = request.env['res.config.settings'].sudo().get_values()
        values = {
            "settings": settings
        }
        return request.render('wbl_odoo_marketplace.marketplace_seller_marketing', values)

    @http.route('/become/seller', auth='public', website=True)
    def become_seller(self):
        countries = request.env['res.country'].sudo().search([])
        user_id = request.env['res.users'].sudo().browse(request.session.uid)
        values = {
            "countries": countries,
            "partner": user_id.partner_id
        }
        if request.session.uid:
            return request.render('wbl_odoo_marketplace.marketplace_become_seller', values)
        return request.redirect('/web/login')

    @http.route('/custom_dashboard/user_groups', type='json', auth='user')
    def get_user_groups(self):
        user = request.env.user
        # Check if the user is an Administrator
        currency_symbol = user.company_id.currency_id.symbol
        is_admin = user.has_group('base.group_system')
        return {'is_admin': is_admin, 'currency_symbol': currency_symbol}

    @http.route('/seller/form', type='json', auth='public', website=True)
    def become_seller_form(self, seller_name, seller_phone, seller_email, seller_country_id, shop_name, shop_url):
        user_id = request.env['res.users'].sudo().browse(request.session.uid)

        existing_seller = request.env['marketplace.seller'].sudo().search([('user_id', '=', user_id.id)])
        if existing_seller:
            return {'URL': 'seller_exist'}

        if request.env['marketplace.seller'].sudo().search([('shop_url', '=', shop_url)]):
            return {'URL': 'shop_url_exist'}

        form_data = {
            'user_id': user_id.id,
            'name': seller_name,
            'phone': seller_phone,
            'email': seller_email,
            'country_id': seller_country_id,
            'shop_name': shop_name,
            'shop_url': shop_url,
        }
        seller = request.env['marketplace.seller'].sudo().create(form_data)
        user_id.partner_id.write({'seller_id': seller.id})
        group_id = request.env.ref('wbl_odoo_marketplace.group_marketplace_pending_seller')
        user_id.write({'groups_id': [
            (3, request.env.ref('base.group_portal').id),
            (4, request.env.ref('base.group_user').id),
            (4, group_id.id)
        ]})

        # Send mail
        self._notify_seller_approval_request(seller.id)

        # Seller Auto Approval
        auto_approval = request.env['ir.config_parameter'].sudo().get_param('wbl_odoo_marketplace.seller_auto_approval')
        if auto_approval == 'True':
            approved_group_id = request.env.ref('wbl_odoo_marketplace.group_marketplace_seller')
            user_id.write({'groups_id': [(4, approved_group_id.id)]})
            seller.state = 'approved'

        return {"URL": '/web#action=wbl_odoo_marketplace.action_client_marketplace_menu'}

    @http.route('/seller/profile/<string:shop_url>', auth='public', website=True)
    def seller_profile(self, shop_url, search=None):
        values = {}
        if shop_url:
            # Fetch the seller based on the shop URL
            mp_seller = request.env['marketplace.seller'].sudo().search([('shop_url', 'ilike', shop_url)], limit=1)
            if mp_seller:
                # Search for seller products with optional name filtering
                product_domain = [
                    ('seller_id', '=', mp_seller.id),
                    ('state', '=', 'approved')
                ]
                if search:
                    product_domain.append(('name', 'ilike', search))

                seller_products = request.env['mp.seller.product'].sudo().search(product_domain)
                user_id = request.env['res.users'].sudo().browse(request.session.uid)

                # Add seller and product data to values
                values['seller'] = mp_seller
                values['products'] = seller_products
                values['search'] = search
                values['partner'] = user_id.partner_id
                values['search'] = search
            else:
                values['error'] = "Seller not found"

        return request.render('wbl_odoo_marketplace.marketplace_seller_profile', values)

    @http.route('/contact/seller', auth='public', type="json", website=True)
    def contact_seller(self, name, phone, email, subject, question, seller_id, seller_uid):
        user_id = request.env['res.users'].sudo().browse(request.session.uid)
        existing_customer_query = request.env['marketplace.customer.query'].sudo().search(
            [('partner_id', '=', user_id.partner_id.id), ('state', '=', 'processing')])
        if existing_customer_query:
            return {'URL': 'exist'}
        form_data = {
            'partner_id': user_id.partner_id.id,
            'seller_id': int(seller_id),
            'seller_uid': int(seller_uid),
            'name': name,
            'email': email,
            'phone': phone,
            'subject': subject,
            'question': question,
        }
        if request.session.uid:
            new_query = request.env['marketplace.customer.query'].sudo().create(form_data)
            self._customer_query_mail(new_query)
            seller_id = request.env['marketplace.seller'].sudo().search([('id', '=', seller_id)])
            shop_url = f'/seller/profile/{seller_id.shop_url}'
            return {'URL': shop_url}
        return {'URL': '/web/login'}

    @http.route('/verify/shopUrl', type='json', auth='public', website=True)
    def verify_shop_url(self, shop_url):
        unique_url = request.env['marketplace.seller'].sudo().search([('shop_url', '=', shop_url)])
        if unique_url:
            return True
        else:
            return False

    @http.route('/seller/query', type="json", auth='public', website=True)
    def seller_query(self, name, email, topic, message):
        user_id = request.env['res.users'].sudo().browse(request.session.uid)
        existing_seller_query = request.env['marketplace.seller.query'].sudo().search(
            [('partner_id', '=', user_id.partner_id.id), ('state', '=', 'pending')])
        if existing_seller_query:
            return {'URL': 'exist'}
        # Prepare data for saving
        form_data = {
            'partner_id': user_id.partner_id.id,
            'name': name,
            'contact_info': email,
            'topic': topic,
            'message': message,
        }
        # Save the data to the marketplace.seller.query model
        if request.session.uid:
            new_query = request.env['marketplace.seller.query'].sudo().create(form_data)
            self._seller_query_mail(new_query)
            return {'URL': '/seller/marketing'}
        # Redirect to marketing page
        return {'URL': '/web/login'}

    def _notify_seller_approval_request(self, seller_id):
        settings = request.env['ir.config_parameter'].sudo()
        notify_admin = settings.get_param('wbl_odoo_marketplace.seller_request_notify_to_admin')
        notify_seller = settings.get_param('wbl_odoo_marketplace.seller_request_notify_to_seller')

        # Send email to admin if notify_admin is True
        if notify_admin:
            template = request.env.ref('wbl_odoo_marketplace.mail_template_seller_request_sent')
            template.send_mail(seller_id, force_send=True)

        # Send email to seller if notify_seller is True
        if notify_seller:
            template = request.env.ref('wbl_odoo_marketplace.mail_template_seller_account_submission_admin')
            template.send_mail(seller_id, force_send=True)

    def _customer_query_mail(self, new_query):
        settings = request.env['ir.config_parameter'].sudo()
        notify_seller = settings.get_param('wbl_odoo_marketplace.customer_query_notify_to_seller')
        notify_customer = settings.get_param('wbl_odoo_marketplace.customer_query_notify_to_customer')
        if notify_seller:
            template = request.env.ref('wbl_odoo_marketplace.mail_sent_a_email_to_seller_for_query_template')
            template.send_mail(new_query.id, force_send=True)

        if notify_customer:
            template = request.env.ref('wbl_odoo_marketplace.mail_template_customer_query_sent_template')
            template.send_mail(new_query.id, force_send=True)

        email_values = {
            'email_to': new_query.seller_uid.company_id.email,
            'email_from': new_query.email
        }
        template = request.env.ref('wbl_odoo_marketplace.mail_sent_a_email_to_seller_for_query_template')
        template.send_mail(new_query.id, force_send=True, email_values=email_values)

    def _seller_query_mail(self, new_query):
        template = request.env.ref('wbl_odoo_marketplace.mail_sent_a_email_to_seller_for_seller_query_template')
        template.send_mail(new_query.id, force_send=True)
        template = request.env.ref('wbl_odoo_marketplace.mail_sent_a_email_to_admin_for_seller_query_template')
        template.send_mail(new_query.id, force_send=True)
