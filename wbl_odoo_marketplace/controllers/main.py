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

    @http.route('/seller/form', type='http', auth='public', website=True, methods=['POST'])
    def become_seller_form(self, **post):
        user_id = request.env['res.users'].sudo().browse(request.session.uid)
        # Check if the shop URL is unique
        shop_url = post.get('shop_unique_url')
        if request.env['marketplace.seller'].sudo().search([('shop_url', '=', shop_url)]):
            print('hello')
            return request.redirect('/become/seller')

        form_data = {
            'user_id': user_id.id,
            'name': post.get('seller_name'),
            'phone': post.get('seller_phone'),
            'email': post.get('seller_email'),
            'country_id': post.get('seller_country_id'),
            'shop_name': post.get('shop_name'),
            'shop_url': post.get('shop_unique_url'),
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

        return request.redirect('/web#action=wbl_odoo_marketplace.action_client_marketplace_menu')

    @http.route('/seller/profile/<string:shop_url>', auth='public', website=True)
    def seller_profile(self, shop_url, search=None):
        print(search)
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

    @http.route('/contact/seller', auth='public', website=True)
    def contact_seller(self, **post):
        user_id = request.env['res.users'].sudo().browse(request.session.uid)
        form_data = {
            'partner_id': user_id.partner_id.id,
            'seller_id': post.get('seller_id'),
            'seller_uid': post.get('seller_uid'),
            'name': post.get('partner_name'),
            'email': post.get('partner_email'),
            'phone': post.get('partner_phone'),
            'subject': post.get('subject'),
            'question': post.get('question'),
        }
        customer_query = request.env['marketplace.customer.query'].sudo().create(form_data)
        return request.redirect('/')

    @http.route('/verify/shopUrl', type='json', auth='public', website=True)
    def verify_shop_url(self, shop_url):
        unique_url = request.env['marketplace.seller'].sudo().search([('shop_url', '=', shop_url)])
        if unique_url:
            return True
        else:
            return False

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
