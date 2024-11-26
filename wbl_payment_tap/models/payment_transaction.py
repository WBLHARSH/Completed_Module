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
import uuid
import hashlib
import hmac
import json
import requests
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
import logging
from urllib.parse import urlparse, parse_qs

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    tap_transaction_id = fields.Char(
        string="Tap Transaction ID",
        readonly=True,
    )

    tap_transaction_currency = fields.Char(
        string="Tap Transaction Currency",
        readonly=True,
    )

    tap_transaction_status = fields.Char(
        string="Tap Transaction Status",
        readonly=True,
    )

    from urllib.parse import urlparse, parse_qs

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)

        if self.provider_code != 'tap':
            return res

        response = self.send_payment(self.reference)

        # Parse the URL and extract the query parameters
        parsed_url = urlparse(response)
        query_params = parse_qs(parsed_url.query)

        # Extract the 'mode' parameter from the query params
        mode = query_params.get('mode', [''])[0]
        theme_mode = query_params.get('themeMode', [''])[0]
        language = query_params.get('language', [''])[0]
        token = query_params.get('token', [''])[0]

        # Return the response including the 'mode' value
        return {
            'api_url': response,
            'mode': mode,  # Add the extracted 'mode' parameter to the return values
            'theme_mode': theme_mode,  # Add the extracted 'mode' parameter to the return values
            'language': language,  # Add the extracted 'mode' parameter to the return values
            'token': token,  # Add the extracted 'mode' parameter to the return values
            'reference': self.reference,
        }

    def send_payment(self,reference):
        provider = self.env['payment.provider'].search([('code', '=', 'tap')], limit=1)
        if not provider:
            raise UserError(_("Payment provider for tap not found."))
        url = "https://api.tap.company/v2/charges/"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {provider.tap_secret_key}"
        }
        base_url = self.provider_id.get_base_url()
        success_url = "payment/tap/redirect"
        payload = {
            "amount": self.amount,
            "currency": self.currency_id.name,
            "customer_initiated": True,
            "threeDSecure": provider.three_d_secure,
            "save_card": False,
            "description": f"Payment for Order {self.reference} by {self.partner_id.name}",
            "metadata": {
                "udf1": "Order ID: " + str(self.reference),
                "udf2": "Customer ID: " + str(self.partner_id.id),
                "udf3": "Transaction ID: " + str(self.id),
                "udf4": "Payment Provider: Tap",
                "udf5": "Any additional data you want"
            },
            "reference": {
                "transaction": str(uuid.uuid4()),  # Unique transaction ID for this charge
                "order": self.reference  # Use the actual transaction reference
            },
            "receipt": {
                "email": True,
                "sms": True
            },
            "customer": {
                "first_name": self.partner_id.name.split()[0],
                "middle_name": self.partner_id.name.split()[1] if len(self.partner_id.name.split()) > 2 else '',
                "last_name": self.partner_id.name.split()[-1],
                "email": self.partner_id.email,
                "phone": {
                    "country_code": self.partner_id.country_id.phone_code,
                    "number": self.partner_id.mobile
                }
            },
            "source": {
                "id": "src_card"  # Assuming a card is being used for the transaction
            },
            "redirect": {
                "url": f"{base_url}{success_url}?reference={reference}"  # Replace with your actual redirect URL
            }
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            url = response_json['transaction']['url']
            return url
        else:
            raise Exception(f"Payment failed: {response.status_code} - {response.text}")


    def _get_tx_from_notification_data(self, provider_code, notification_data):

        """Override of payment to find the transaction based on tap data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != "tap" or len(tx) == 1:
            return tx

        reference = notification_data.get("reference")

        tx = self.search(
            [("reference", "=", reference), ("provider_code", "=", "tap")]
        )
        if not tx:
            raise ValidationError(
                "tap: "
                + _("No transaction found matching reference %s.", reference)
            )

        return tx
    #
    def _tap_form_validate(self, data):
        _logger.debug(f"Airwallex response data: {data}")
        payment_chg_id = data.get('tap_id')
        provider = self.env['payment.provider'].search([('code', '=', 'tap')], limit=1)
        if not payment_chg_id:
            raise ValidationError("No payment_intent_id found in the response.")

        # Fetch additional data from Airwallex API using payment_intent_id
        api_url = f"https://api.tap.company/v2/charges/{payment_chg_id}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {provider.tap_secret_key}"
        }

        response = requests.get(api_url, headers=headers)
        payment_data = response.json()

        res = {
            "tap_transaction_id": payment_data.get('id'),
            "provider_reference": payment_data.get('id'),
            "tap_transaction_currency": payment_data.get('currency'),
            "tap_transaction_status": payment_data.get('status'),
        }
        self.write(res)
        tap_status = payment_data.get('status')
        if tap_status in ["pending", "delayed"]:
            self._set_pending()
        elif tap_status == "CAPTURED":
            self._set_done()
        else:
            self._set_canceled()

    def _process_notification_data(self, notification_data):

        """Override of payment to process the transaction based on tap data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        _logger.debug(f"Received notification data:\n{notification_data}")
        super()._process_notification_data(notification_data)
        if self.provider_code != "tap":
            return

        self._tap_form_validate(notification_data)
