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

from odoo import models, fields, api
from odoo.http import request
from geopy.distance import great_circle



class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    def _get_price_dict(self, total, weight, volume, quantity):
        # Call the super method to get the price dict
        response = super()._get_price_dict(total=total, weight=weight, volume=volume, quantity=quantity)
        settings = request.env['res.config.settings'].sudo().get_values()
        if settings['geopy_measure_method']:
            print('helllpo world')
            order = request.website.sale_get_order()
            if order:
                response.update({'distance': float(
                    order.distance_amount) if order.distance_amount else self._get_shipping_distance()})
            else:
                response.update({'distance': 0.0})
        else:
            response.update({'distance': 0.0})
        return response

    def _get_shipping_distance(self):
        """Calculate the total unique shipping distance for the order."""
        carrier_rule = self.price_rule_ids.filtered(lambda r: r.variable == 'distance')
        if not carrier_rule:
            return 0.0  # No distance rule found

        order = request.website.sale_get_order()
        partner_shipping = order.partner_shipping_id
        shipping_lat_long = self._get_cached_geolocation(partner_shipping)
        print(shipping_lat_long)

        if not shipping_lat_long:
            return 0.0  # Invalid shipping address

        # Initialize total distance
        total_distance = 0.0
        geolocation_cache = {}

        for line in order.order_line.filtered(
                lambda l: l.state != 'cancel' and not l.is_delivery and l.product_id and l.product_id.type != 'service'):
            warehouse_partner = line.product_id.property_stock_inventory.company_id.partner_id
            warehouse_lat_long = self._get_cached_geolocation(warehouse_partner, geolocation_cache)

            if warehouse_lat_long:
                # Calculate the distance and accumulate
                distance = great_circle(warehouse_lat_long, shipping_lat_long).km
                total_distance += distance

        # Get the distance unit from the carrier rule
        distance_unit = carrier_rule[0].distance_unit if carrier_rule else 'km'

        # Convert the distance to the selected unit
        if distance_unit == 'miles':
            total_distance = total_distance * 0.621371  # Convert km to miles

        # Store total distance in the order and return it
        order.distance_amount = str(round(total_distance, 2))
        return total_distance

    def _get_cached_geolocation(self, partner, cache={}):
        """Helper method to cache geolocation lookups."""
        address_key = f"{partner.street}-{partner.zip}-{partner.city}-{partner.state_id.name}-{partner.country_id.name}"

        if address_key not in cache:
            cache[address_key] = partner._geo_localize(partner.street, partner.zip, partner.city, partner.state_id.name,
                                                       partner.country_id.name)
            print(cache[address_key])
        return cache[address_key]

    def get_warehouse_from_product(self, product_id):
        """Retrieve warehouse associated with the product's stock location."""
        if not product_id:
            return None

        stock_quant = self.env['stock.quant'].sudo().search([('product_id', '=', product_id.id)], limit=1)
        if stock_quant and stock_quant.location_id:
            warehouse = self.env['stock.warehouse'].sudo().search([('lot_stock_id', '=', stock_quant.location_id.id)],
                                                                  limit=1)
            if warehouse:
                return warehouse
        return None
