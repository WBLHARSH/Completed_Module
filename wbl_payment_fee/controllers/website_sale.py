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

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request


class WebsiteSaleInherit(WebsiteSale):
    @http.route('/shop/payment', type='http', auth='public', website=True, sitemap=False)
    def shop_payment(self, **post):
        # Call the super to maintain the existing behavior
        response = super(WebsiteSaleInherit, self).shop_payment(**post)

        # Fetch payment providers that are either in 'test' or 'enabled' state
        providers = request.env['payment.provider'].search([
            ('state', 'in', ['test', 'enabled']),
            ('enable_payment_fee', '=', True)
        ])

        # Create a dictionary mapping payment method IDs to their corresponding fee amount or percentage
        providers_list = {
            provider.payment_method_ids.id: {
                'fee_type': provider.fee,  # 'fixed_amount' or 'order_percentage'
                'fee_amount': provider.fee_amount,
                'fee_percentage': provider.fee_percentage * 100
            }
            for provider in providers
        }

        # Add this mapping to the context so it's available in the template
        response.qcontext.update({
            'providers': providers_list,  # Mapping of payment method ID to fee type, amount, and percentage
        })

        return response
