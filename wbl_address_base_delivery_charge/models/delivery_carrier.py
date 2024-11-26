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

from odoo import _, fields, models, api
from odoo.http import request
import psycopg2  # Importing the PostgreSQL-specific exception class


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    calc_distance_prc = fields.Boolean(string="Calculate Distance Price", default=False)

    def rate_shipment(self, order):
        response = super(DeliveryCarrier, self).rate_shipment(order=order)
        if self.calc_distance_prc:
            order = request.website.sale_get_order(force_create=True)
            partner_shipping = order.partner_shipping_id
            partner_abidjan_id = partner_shipping.abidjan
            partner_ivory_coast_id = partner_shipping.ivory_coast
            partner_country_id = partner_shipping.country
            additional_price = 0

            if partner_shipping.selected_option == 'Abidjan' and partner_abidjan_id:
                additional_price = partner_abidjan_id.price
            elif partner_shipping.selected_option == 'Ivory Coast' and partner_ivory_coast_id:
                additional_price = partner_ivory_coast_id.price
            elif partner_shipping.selected_option == 'Countries' and partner_country_id:
                additional_price = partner_country_id.price

            final_delivery_price = response['price'] + additional_price
            order.set_delivery_line(self, final_delivery_price)
            response.update({
                'price': final_delivery_price,
                'carrier_price': final_delivery_price,
            })
        return response
