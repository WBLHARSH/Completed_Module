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
import uuid,requests


class MyAirwallexController(http.Controller):
    _success_url = "/payment/airwallex/return"
    _cancel_url = "/payment/airwallex/cancel"

    @http.route('/airwallex/payment/intent', type='json', auth='public', website=True)
    def airwallexIntent(self, paymentIntent=None):
        if paymentIntent == True:
            provider = request.env['payment.provider'].search([('code', '=', 'airwallex')], limit=1)
            bearerToken = provider.bearerToken()
            order = request.website.sale_get_order()
            partner = request.env.user.partner_id
            partner_name = partner.name.split(" ", 1)
            first_name = partner_name[0]
            last_name = partner_name[1] if len(partner_name) > 1 else ""
            current_website_name = request.env['website'].sudo().get_current_website().name
            products = []
            for line in order.order_line:
                quantity = int(line.product_uom_qty) if line.product_uom_qty > 0 else 1  # Default to 1 if invalid
                product_data = {
                    "category": line.product_id.categ_id.name,
                    "code": line.product_id.default_code or "",
                    "desc": line.product_id.name,
                    "image_url": line.product_id.image_1920 and f"/web/image/product.product/{line.product_id.id}/image_1920",
                    "name": line.product_id.name,
                    "quantity": quantity,
                    "seller": {
                        "identifier": str(partner.id),
                        "name": partner.name,
                    },
                    "sku": line.product_id.default_code or "",
                    "type": "physical",
                    "unit_price": line.price_unit,
                    "url": f"/shop/product/{line.product_id.id}"
                }
                products.append(product_data)
            payment_intent_url = "https://api-demo.airwallex.com/api/v1/pa/payment_intents/create"
            payment_intent_headers = {
                "Authorization": f"Bearer {bearerToken}",
                "Content-Type": "application/json"
            }
            payment_intent_data = {
                "amount": str(order.amount_total),
                "currency": order.currency_id.name,
                "customer": {
                    "address": {
                        "city": partner.city,
                        "country_code": partner.country_id.code,
                        "postcode": partner.zip,
                        "state": partner.state_id.name,
                        "street": partner.street
                    },
                    "email": partner.email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "phone_number": partner.phone,
                },
                "descriptor": current_website_name,
                "merchant_order_id": order.name,
                "order": {
                    "products": products,
                    "type": "physical_goods",
                },
                "payment_method_options": {
                    "card": {
                        "risk_control": {
                            "skip_risk_processing": False,
                            "three_domain_secure_action": "FORCE_3DS",
                            "three_ds_action": "FORCE_3DS"
                        },
                        "three_ds_action": "FORCE_3DS"
                    }
                },
                "request_id": str(uuid.uuid4()),
                "return_url": "http://localhost:8050/payment/airwallex/return"
            }
            payment_intent_response = requests.post(payment_intent_url, headers=payment_intent_headers,
                                                    json=payment_intent_data)
            if payment_intent_response.status_code == 201:
                payment_intent = payment_intent_response.json()
                return {
                    'intent_id': payment_intent.get('id'),
                    'client_secret': payment_intent.get('client_secret'),
                    "currency": order.currency_id.name,
                }
            else:
                return {
                    'result': 'fail',
                }

    @http.route([_success_url, _cancel_url], type='http', auth='public', methods=['GET', 'POST'], csrf=False,
                save_session=False)
    def airwallex_return_from_checkout(self, **data):
        request.env['payment.transaction'].sudo()._handle_notification_data('airwallex', data)
        return request.redirect('/payment/status')
