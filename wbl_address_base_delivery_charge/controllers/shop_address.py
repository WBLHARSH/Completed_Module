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
from odoo import http, _
from odoo.http import request
import random


class WebsiteSaleInherit(WebsiteSale):

    # @http.route('/shop/payment', type='http', auth='public', website=True, sitemap=False)
    # def shop_payment(self, **post):
    #     response = super(WebsiteSaleInherit, self).shop_payment(**post)
    #     return response

    # ===================== Save Hard Code Data In Address Form =========================
    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True,
                sitemap=False)
    def address(self, **kw):
        # Ensure required fields are filled
        order = request.website.sale_get_order()
        order._remove_delivery_line()
        if not kw.get('city'):
            kw['city'] = 'Ghaziabad'
        if not kw.get('street'):
            kw['street'] = '10'
        if not kw.get('zip'):
            kw['zip'] = '201301'

        # Ensure the country_id is filled with a default value (United States in this example)
        united_states = request.env['res.country'].sudo().search([('id', '=', '44')], limit=1)
        if united_states and not kw.get('country_id'):
            kw['country_id'] = united_states.id

        # Ensure state_id is filled with a random state from the United States
        if united_states and not kw.get('state_id'):
            us_states = request.env['res.country.state'].sudo().search([('country_id', '=', united_states.id)])
            if us_states:
                random_state = random.choice(us_states)
                kw['state_id'] = random_state.id
        # Call the super to maintain existing behavior
        response = super(WebsiteSaleInherit, self).address(**kw)

        # Get custom settings and update qcontext
        settings = request.env['res.config.settings'].sudo().get_values()
        response.qcontext.update({
            'abidjans': settings['abidjans'],
            'ivory_coast': settings['ivory_coast'],
            'countries': settings['countries']
        })
        return response

    def _get_mandatory_fields_shipping(self, country_id=False):
        response = super(WebsiteSaleInherit, self)._get_mandatory_fields_shipping(country_id=country_id)
        response += ['address', 'selected_option']
        return response

    def _get_mandatory_fields_billing(self, country_id=False):
        response = super(WebsiteSaleInherit, self)._get_mandatory_fields_shipping(country_id=country_id)
        response += ['address', 'selected_option']
        return response

    # ===================== Save Address Form Data ========================
    def _checkout_form_save(self, mode, checkout, all_values):
        # Call the super method to get the response
        response = super(WebsiteSaleInherit, self)._checkout_form_save(mode=mode, checkout=checkout,
                                                                       all_values=all_values)

        # Get the partner_id from the response
        partner_id = response
        partner = request.env['res.partner'].sudo().browse(partner_id)
        # Prepare the values to write
        update_values = {}

        # Check and prepare the abidjan field if present
        if all_values.get("abidjans_id") and all_values.get("selected_option") == 'Abidjan':
            update_values['abidjan'] = int(all_values["abidjans_id"])  # Ensure it's an integer
            update_values['ivory_coast'] = None  # Ensure it's an integer
            update_values['country'] = None  # Ensure it's an integer
        # Check and prepare the ivory_coast field if present
        if all_values.get("ivory_coast_id") and all_values.get("selected_option") == 'Ivory Coast':
            update_values['ivory_coast'] = int(all_values["ivory_coast_id"])  # Ensure it's an integer
            update_values['abidjan'] = None
            update_values['country'] = None
            # Check and prepare the country field if present
        if all_values.get("countries_id") and all_values.get("selected_option") == 'Countries':
            update_values['country'] = int(all_values["countries_id"])  # Ensure it's an integer
            update_values['abidjan'] = None
            update_values['ivory_coast'] = None  # Ensure it's an integer
        # Save the address field directly from all_values
        if all_values.get("address"):  # Check if the address field is present
            update_values['address'] = all_values["address"]

        if all_values.get("selected_option"):  # Check if the address field is present
            update_values['selected_option'] = all_values["selected_option"]

        # Perform the write operation if there are any values to update
        if update_values:
            try:
                partner.write(update_values)  # Use write to update the partner record
            except Exception as e:
                print("Error updating partner fields:", e)  # Log the error message for debugging
        return response  # Return the response

    def checkout_form_validate(self, mode, all_form_values, data):
        # Call the parent method to get the base validation response
        error, error_message = super(WebsiteSaleInherit, self).checkout_form_validate(mode=mode,
                                                                                      all_form_values=all_form_values,
                                                                                      data=data)
        # Check if the selected_option is 'Abidjan' and the 'Abidjan' field is None
        if data.get('selected_option') == 'Abidjan' and not data.get('abidjans_id'):
            # Add an error for the 'Abidjan' field
            error['abidjans_id'] = 'missing'
            # Append a custom error message
            error_message.append(_('The Abidjan field is required when the selected option is Abidjan.'))
        elif data.get('selected_option') == 'Ivory Coast' and not data.get('ivory_coast_id'):
            # Add an error for the 'Abidjan' field
            error['ivory_coast_id'] = 'missing'
            # Append a custom error message
            error_message.append(_('The Ivory Coast field is required when the selected option is Ivory Coast.'))
        elif data.get('selected_option') == 'Countries' and not data.get('countries_id'):
            # Add an error for the 'Abidjan' field
            error['countries_id'] = 'missing'
            # Append a custom error message
            error_message.append(_('The Other Country field is required when the selected option is Other Country.'))

        return error, error_message
