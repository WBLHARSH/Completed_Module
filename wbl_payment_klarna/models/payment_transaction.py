# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Subina (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
# Import required libraries (make sure it is installed!)
import logging

import requests
from requests.auth import HTTPBasicAuth

from odoo import models, fields

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    """Inherited class of payment transaction to add klarna functions."""
    _inherit = 'payment.transaction'

    klarna_transaction_id = fields.Char(
        string="Klarna Transaction ID",
        readonly=True,
    )

    klarna_transaction_currency = fields.Char(
        string="Klarna Transaction Currency",
        readonly=True,
    )

    klarna_transaction_status = fields.Char(
        string="Klarna Transaction Status",
        readonly=True,
    )

    def _get_specific_rendering_values(self, processing_values):
        """ Function to fetch the values of the payment gateway"""
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'klarna':
            return res
        return self.send_payment

    @property
    def send_payment(self):
        """Send payment information to Klarna for processing."""
        base_api_url = self.env['payment.provider'].search([('code', '=', 'klarna')])._klarna_get_api_url()
        api_url = f"{base_api_url}checkout/v3/orders"
        api_key = self.env['payment.provider'].search([('code', '=', 'klarna')])

        klarna_username = api_key.klarna_username
        klarna_password = api_key.klarna_password
        odoo_base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        # Get sale order associated with this payment transaction
        sale_order = self.sale_order_ids[0] if self.sale_order_ids else None
        if not sale_order:
            raise ValueError("No sale order linked to the payment transaction.")

        # Partner and Address Information
        partner = self.partner_id
        if not partner:
            raise ValueError("Transaction does not have a partner associated.")

        MobileCountryCode = partner.country_id.phone_code
        phone_number = self.partner_phone
        if not phone_number:
            raise ValueError("Please provide the phone number.")
        else:
            phone_number = phone_number.replace(str(MobileCountryCode), '').strip()
            if phone_number.startswith('+'):
                phone_number = phone_number[1:]
            elif not phone_number:
                raise ValueError("Please provide the phone number in proper format.")

        # Calculate the total amount and tax amount dynamically
        total_amount = int(sale_order.amount_total * 100)  # Assuming Klarna uses the lowest denomination (cents)
        total_tax_amount = int(sale_order.amount_tax * 100)

        # Prepare dynamic order lines data
        order_lines = []
        for line in sale_order.order_line:
            order_line_data = {
                "type": "physical",  # Could be dynamic if necessary
                "reference": line.product_id.default_code or "No Ref",
                "name": line.product_id.name,
                "quantity": int(line.product_uom_qty),
                "quantity_unit": "pcs",
                "unit_price": int(line.price_unit * 100),
                "tax_rate": int(line.tax_id.amount * 100) if line.tax_id else 0,
                "total_amount": int(line.price_subtotal * 100),
                "total_discount_amount": int(line.discount * 100),
                "total_tax_amount": int(line.price_tax * 100) if line.price_tax else 0,
            }
            order_lines.append(order_line_data)

        sendpay_data = {
            "purchase_country": partner.country_id.code,
            "purchase_currency": sale_order.currency_id.name,
            "locale": "en-GB",
            "order_amount": total_amount,
            "order_tax_amount": total_tax_amount,
            "order_lines": order_lines,
            "merchant_urls": {
                "terms": f"{odoo_base_url}/terms",
                "checkout": f"{odoo_base_url}/checkout",
                "confirmation": "https://www.example.com/confirmation.html",
                "push": "https://www.example.com/api/push"
            }
        }

        headers = {
            'Content-Type': 'application/json',
        }
        response = requests.post(api_url, auth=HTTPBasicAuth(klarna_username, klarna_password), headers=headers,
                                 json=sendpay_data)
        response_data = response.json()
        print(response_data)
        if response_data:
            self.klarna_transaction_id = response_data.get("order_id")
            self.klarna_transaction_currency = response_data.get("purchase_currency")
            self.klarna_transaction_status = response_data.get("status")
        return {
            'api_url': f"{odoo_base_url}/payment/klarna/response",
            'data': response_data.get("html_snippet"),
        }

    # def _get_tx_from_notification_data(self, provider_code, notification_data):
    #     """Getting  payment status from klarna"""
    #     api_key = self.env['payment.provider'].search(
    #         [('code', '=', 'klarna')]).klarna_token
    #     base_api_url = self.env['payment.provider'].search(
    #         [('code', '=', 'klarna')])._klarna_get_api_url()
    #     url = f"{base_api_url}v2/GetPaymentStatus"
    #     paymentid = notification_data.get('paymentId')
    #     payload = json.dumps({
    #         "Key": f"{paymentid}",
    #         "KeyType": "paymentId"
    #     })
    #     headers = {
    #         'Content-Type': 'application/json',
    #         'Accept': 'application/json',
    #         'Authorization': f'Bearer {api_key}',
    #     }
    #     response = requests.request("POST", url,
    #                                 headers=headers, data=payload)
    #     response_data = response.json()
    #     tx = super()._get_tx_from_notification_data(provider_code,
    #                                                 notification_data)
    #     if provider_code != 'klarna' or len(tx) == 1:
    #         return tx
    #     domain = [('provider_code', '=', 'klarna')]
    #     reference = ""
    #     if response_data["Data"]["CustomerReference"]:
    #         reference = response_data["Data"]["CustomerReference"]
    #         domain.append(('reference', '=', str(reference)))
    #     if tx := self.search(domain):
    #         return tx
    #     else:
    #         raise ValidationError(
    #             "klarna: " + _(
    #                 "No transaction found matching reference %s.",
    #                 reference)
    #         )
    #
    # def _handle_notification_data(self, provider_code, notification_data):
    #     """Function to handle the notification data """
    #     tx = self._get_tx_from_notification_data(provider_code,
    #                                              notification_data)
    #     tx._process_notification_data(notification_data)
    #     tx._execute_callback()
    #     return tx
    #
    # def _process_notification_data(self, notification_data):
    #     """ Function to process the notification data"""
    #     super()._process_notification_data(notification_data)
    #     if self.provider_code != 'klarna':
    #         return
    #     else:
    #         self._set_done()
