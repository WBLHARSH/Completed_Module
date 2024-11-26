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


from odoo import _, models, fields
import requests
from odoo.exceptions import UserError, ValidationError
import logging
from odoo.http import request

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    payTabs_transaction_id = fields.Char(
        string="PayTabs Transaction ID",
        readonly=True,
    )

    payTabs_transaction_currency = fields.Char(
        string="PayTabs Transaction Currency",
        readonly=True,
    )

    payTabs_transaction_status = fields.Char(
        string="PayTabs Transaction Status",
        readonly=True,
    )

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)

        if self.provider_code != 'payTabs':
            return res
        response = self.send_payment(self.reference)
        return {
            'api_url': response,
            'reference': self.reference,
        }

    def _get_client_ip(self):
        """Retrieve the client's IP address from the current request."""
        if request:
            ip = request.httprequest.remote_addr
            return ip
        return "127.0.0.1"  # Fallback to localhost if IP cannot be determined

    def send_payment(self, reference):
        provider = self.env['payment.provider'].search([('code', '=', 'payTabs')], limit=1)
        if not provider:
            raise UserError(_("Payment provider for payTabs not found."))
        url = "https://secure-global.paytabs.com/payment/request"
        headers = {
            'authorization': provider.payTabs_secret_key,
            'content-type': 'application/json'
        }
        base_url = self.provider_id.get_base_url()
        success_url = "payment/payTabs/redirect"
        payload = {
            'profile_id': provider.payTabs_profile_id,
            'tran_type': 'sale',  # Type of transaction (e.g., sale or authorize)
            'tran_class': 'ecom',  # Transaction class, e-commerce in this case
            'cart_id': str(self.reference),  # Unique cart or transaction reference ID
            'cart_description': f"Payment for Order {self.reference} by {self.partner_id.name}",
            'cart_currency': self.currency_id.name,  # Currency of the transaction
            'cart_amount': self.amount,  # Total amount for the payment
            'callback': f"{base_url}{success_url}?reference={reference}",  # URL for asynchronous callback
            'return': f"{base_url}{success_url}?reference={reference}",  # URL to redirect customer after payment
            "customer_details": {
                "name": self.partner_id.name,  # Customer name
                "email": self.partner_id.email,  # Customer email
                "phone": self.partner_id.phone or "",  # Customer phone
                "street1": self.partner_id.street or "N/A",  # Customer street address
                "city": self.partner_id.city or "N/A",  # Customer city
                "state": self.partner_id.state_id.name if self.partner_id.state_id else "N/A",  # Customer state
                "country": self.partner_id.country_id.code or "N/A",  # Customer country code
                "zip": self.partner_id.zip or "00000",  # Customer postal code
                "ip": self._get_client_ip()
            },
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            url = response_json['redirect_url']
            self.payTabs_transaction_id = response_json['tran_ref']
            return url
        else:
            raise Exception(f"Payment failed: {response.status_code} - {response.text}")

    def _get_tx_from_notification_data(self, provider_code, notification_data):

        """Override of payment to find the transaction based on payTabs data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != "payTabs" or len(tx) == 1:
            return tx

        reference = notification_data.get("reference")
        tx = self.search(
            [("reference", "=", reference), ("provider_code", "=", "payTabs")]
        )
        if not tx:
            raise ValidationError(
                "payTabs: "
                + _("No transaction found matching reference %s.", reference)
            )

        return tx

    def _payTabs_form_validate(self, data):
        _logger.debug(f"payTabs response data: {data}")

        try:
            # Fetch the payment provider configuration
            provider = self.env['payment.provider'].search([('code', '=', 'payTabs')], limit=1)
            if not provider:
                raise ValueError("PayTabs provider not found.")

            # Fetch additional data from payTabs API using payment_intent_id
            _logger.info(f"Transaction ID: {self.payTabs_transaction_id}")

            api_url = "https://secure-global.paytabs.com/payment/query"
            headers = {
                'authorization': provider.payTabs_secret_key,
                'content-type': 'application/json'
            }
            payload = {
                'profile_id': provider.payTabs_profile_id,
                "tran_ref": self.payTabs_transaction_id
            }

            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()  # Raises an error if the response status is not 200 OK

            payment_data = response.json()
            _logger.debug(f"PayTabs API response: {payment_data}")

            # Validate if transaction IDs match
            if self.payTabs_transaction_id == payment_data.get('tran_ref'):
                res = {
                    "provider_reference": payment_data.get('tran_ref'),
                    "payTabs_transaction_currency": payment_data.get('cart_currency'),
                    "payTabs_transaction_status": payment_data['payment_result']['response_message'],
                }
                self.write(res)

                payTabs_status = payment_data['payment_result']['response_status']

                # Handle different payment statuses
                if payTabs_status in ["pending", "delayed"]:
                    self._set_pending()
                elif payTabs_status == "A":
                    self._set_done()
                else:
                    self._set_canceled()
            else:
                _logger.error("Transaction ID mismatch.")
                raise ValueError("PayTabs transaction reference mismatch.")

        except requests.RequestException as e:
            _logger.error(f"Error in PayTabs API request: {e}")
            self._set_canceled()

        except Exception as e:
            _logger.error(f"Error during PayTabs validation: {e}")
            self._set_canceled()

    def _process_notification_data(self, notification_data):

        """Override of payment to process the transaction based on payTabs data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        _logger.debug(f"Received notification data:\n{notification_data}")
        super()._process_notification_data(notification_data)
        if self.provider_code != "payTabs":
            return

        self._payTabs_form_validate(notification_data)
