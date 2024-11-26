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
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from datetime import datetime, timedelta


class WebsiteSaleInherit(WebsiteSale):
    @http.route('/shop/payment', type='http', auth='public', website=True, sitemap=False)
    def shop_payment(self, **post):

        response = super(WebsiteSaleInherit, self).shop_payment(**post)
        settings = request.env['res.config.settings'].sudo().get_values()
        current_website = request.website
        setting_website_id = settings["website"]

        if current_website.id == setting_website_id:
            response.qcontext.update({
                'enable_order_message_field': settings.get("enable_order_message_field", False),
                'enable_desire_date_field': settings.get("enable_desire_date_field", False),
                'minimum_desire': settings.get("minimum_number_of_days", 0),
                'maximum_desire': settings.get("maximum_number_of_days", 0),
            })
        return response

    @http.route('/save_delivery', type='json', auth='public', website=True)
    def save_delivery(self, order_message_field=None, desire_date_field=None):
        if order_message_field or desire_date_field:
            order = request.website.sale_get_order()

            redirection = self.checkout_redirection(order)
            if redirection:
                return redirection
            if order and order.id:
                order.write({'order_message_field': order_message_field})
                order.write({'desire_date_field': desire_date_field})

        return True

