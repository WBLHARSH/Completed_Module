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


from odoo import http, _
from odoo.http import request
from datetime import datetime


class ProviderDetail(http.Controller):
    @http.route('/provider/detail', type='json', auth='public', website=True)
    def provider_detail(self, provider_id):
        if not provider_id:
            return {}

        payment_provider = request.env['payment.provider'].browse(provider_id)
        order = request.website.sale_get_order(force_create=True)
        currency = order.currency_id
        monetary = request.env['ir.qweb.field.monetary']

        def get_order_data(fee_amount):
            order._create_payment_fee_line(payment_provider, fee_amount)
            order.payment_fee = fee_amount
            return {
                'is_payment_fee': True,
                'new_subtotal_amount': monetary.value_to_html(order.amount_untaxed, {'display_currency': currency}),
                'new_amount_tax': monetary.value_to_html(order.amount_tax, {'display_currency': currency}),
                'new_amount_total': monetary.value_to_html(order.amount_total, {'display_currency': currency}),
                'payment_fee': monetary.value_to_html(fee_amount, {'display_currency': currency}),
            }

        # customer Filter
        partner_ids = payment_provider.partner_ids
        order_partner_id = order.partner_id.id
        partner_match = any(partner_id.id == order_partner_id for partner_id in partner_ids)

        # Product Filter
        product_ids = payment_provider.products_ids
        order_product_ids = order.order_line.mapped('product_id.id')
        product_match = any(product_id.id in order_product_ids for product_id in product_ids)

        # Country Filter
        country_ids = payment_provider.country_ids
        order_country_id = order.partner_id.country_id.id
        country_match = any(country_id.id == order_country_id for country_id in country_ids)

        # Website Filter
        website_ids = payment_provider.website_ids
        order_website_id = request.env['website'].sudo().get_current_website().id
        website_match = any(website_id.id == order_website_id for website_id in website_ids)

        # Calender Filter
        date_match = False
        from_date = payment_provider.from_date or None
        to_date = payment_provider.to_date or None
        current_date = datetime.now().date()
        if from_date and to_date:
            date_match = from_date <= current_date <= to_date

        # Minimum Order Filter
        minimum_order_amount = payment_provider.minimum_order_amount
        tax_excluded = payment_provider.tax_excluded
        if tax_excluded and minimum_order_amount:
            minimum_order_amount_match = order.amount_untaxed >= minimum_order_amount
        elif not tax_excluded and minimum_order_amount:
            minimum_order_amount_match = order.amount_total >= minimum_order_amount
        else:
            minimum_order_amount_match = False

        if product_match or partner_match or country_match or website_match or date_match or minimum_order_amount_match:
            if order and payment_provider.enable_payment_fee:
                order._remove_payment_fee_line()

                if payment_provider.fee == 'fixed_amount':
                    fee_amount = payment_provider.fee_amount
                else:
                    fee_amount = payment_provider.fee_percentage * order.amount_untaxed

                return get_order_data(fee_amount)

        order._remove_payment_fee_line()
        return {
            'is_payment_fee': False,
            'new_subtotal_amount': monetary.value_to_html(order.amount_untaxed, {'display_currency': currency}),
            'new_amount_tax': monetary.value_to_html(order.amount_tax, {'display_currency': currency}),
            'new_amount_total': monetary.value_to_html(order.amount_total, {'display_currency': currency}),
        }
