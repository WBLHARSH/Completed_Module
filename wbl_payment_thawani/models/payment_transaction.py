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
from werkzeug.utils import redirect

from odoo import _, models, fields
import requests, uuid
from odoo.exceptions import UserError, ValidationError
import logging
from werkzeug import urls
from odoo.http import request

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    thawani_transaction_id = fields.Char(
        string="Thawani Transaction ID",
        readonly=True,
    )

    thawani_transaction_currency = fields.Char(
        string="Thawani Transaction Currency",
        readonly=True,
    )

    thawani_transaction_status = fields.Char(
        string="Thawani Transaction Status",
        readonly=True,
    )

    thawani_payment_id = fields.Char(
        string="Thawani Payment Id",
        readonly=True,
    )

    thawani_transaction_type = fields.Char(string='Thawani Payment Type', readonly=True)

    thawani_refund_id = fields.Char(
        string="Thawani Refund ID",
        readonly=True,
    )
    thawani_refund_currency = fields.Char(
        string="Thawani Refund Currency",
        readonly=True,
    )
    thawani_refund_status = fields.Char(
        string="Thawani Refund Status",
        readonly=True,
    )

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)

        if self.provider_code != 'thawani':
            return res
        response = self.send_payment()
        return response

    def send_payment(self):
        provider = self.env['payment.provider'].search([('code', '=', 'thawani')], limit=1)
        base_api_url = provider._thawani_get_api_url()
        if not provider:
            raise UserError(_("Payment provider for Thawani not found."))

        url = f"{base_api_url}api/v1/checkout/session"
        headers = {
            'Content-Type': "application/json",
            'Accept': "application/json",
            'thawani-api-key': provider.thawani_secret_key
        }

        # Dynamic data for the payload
        base_url = self.provider_id.get_base_url()
        success_url = f"{base_url}payment/thawani/success?reference={self.reference}"
        cancel_url = f"{base_url}payment/thawani/cancel?reference={self.reference}"
        customer_name = self.partner_id.name or "Unknown Customer"
        order_id = self.reference

        payload = {
            "client_reference_id": str(uuid.uuid4()),
            "mode": "payment",
            "products": [
                {
                    "name": "product 1",
                    "quantity": 1,
                    "unit_amount": int(self.amount * 1000)
                }
            ],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": {
                "Customer name": customer_name,
                "order id": order_id
            }
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            session_id = response_json['data']['session_id']
            publish_key = provider.thawani_publishable_key
            redirect_url = f"{base_api_url}pay/{session_id}?key={publish_key}"
            parsed_url = urls.url_parse(redirect_url)
            url_params = urls.url_decode(parsed_url.query)
            self.thawani_transaction_id = session_id
            return {
                'api_url': parsed_url.scheme + '://' + parsed_url.netloc + parsed_url.path,
                'url_params': url_params,
            }
        else:
            raise Exception(f"Payment failed: {response.status_code} - {response.text}")

    def _get_tx_from_notification_data(self, provider_code, notification_data):

        """Override of payment to find the transaction based on thawani data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != "thawani" or len(tx) == 1:
            return tx

        reference = notification_data.get("reference")
        tx = self.search(
            [("reference", "=", reference), ("provider_code", "=", "thawani")]
        )
        if not tx:
            raise ValidationError(
                "thawani: "
                + _("No transaction found matching reference %s.", reference)
            )

        return tx

    def _thawani_form_validate(self, data):
        _logger.debug(f"thawani response data: {data}")

        try:
            # Fetch the payment provider configuration
            provider = self.env['payment.provider'].search([('code', '=', 'thawani')], limit=1)
            base_api_url = provider._thawani_get_api_url()
            if not provider:
                raise ValueError("thawani provider not found.")

            # Fetch additional data from thawani API using payment_intent_id
            _logger.info(f"Transaction ID: {self.thawani_transaction_id}")

            api_url = f"{base_api_url}api/v1/checkout/session/{self.thawani_transaction_id}"
            print(api_url)
            headers = {
                'Content-Type': "application/json",
                'Accept': "application/json",
                'thawani-api-key': provider.thawani_secret_key
            }

            response = requests.get(api_url, headers=headers)
            print(response)
            # response.raise_for_status()  # Raises an error if the response status is not 200 OK

            payment_data = response.json()
            print(payment_data)
            _logger.debug(f"thawani API response: {payment_data}")

            # Validate if transaction IDs match
            if self.thawani_transaction_id == payment_data['data']['session_id']:
                thawani_status = payment_data['data']['payment_status']

                # Handle different payment statuses
                if thawani_status in ["pending", "delayed"]:
                    self._set_pending()
                elif thawani_status == "paid":
                    self._set_done()
                    invoice_id = payment_data['data']['invoice']
                    payment_id = self._thawani_payment_id(invoice_id, base_api_url, headers)
                    res = {
                        "provider_reference": payment_data['data']['session_id'],
                        "thawani_transaction_currency": payment_data['data']['currency'],
                        "thawani_transaction_status": thawani_status,
                        'thawani_transaction_type': 'PAYMENT',
                        'thawani_payment_id': payment_id
                    }
                    self.write(res)
                else:
                    self._set_canceled()
                    res = {
                        "provider_reference": payment_data['data']['session_id'],
                        "thawani_transaction_currency": payment_data['data']['currency'],
                        "thawani_transaction_status": thawani_status,
                    }
                    self.write(res)
            else:
                _logger.error("Transaction ID mismatch.")
                self._set_canceled()

        except requests.RequestException as e:
            _logger.error(f"Error in thawani API request: {e}")
            self._set_canceled()

        except Exception as e:
            _logger.error(f"Error during thawani validation: {e}")
            # self._set_canceled()

    def _process_notification_data(self, notification_data):

        """Override of payment to process the transaction based on thawani data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        _logger.debug(f"Received notification data:\n{notification_data}")
        super()._process_notification_data(notification_data)
        if self.provider_code != "thawani":
            return

        self._thawani_form_validate(notification_data)

    def _thawani_payment_id(self, invoice_id, base_api_url, headers):
        url = f"{base_api_url}api/v1/payments?checkout_invoice={invoice_id}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            payment_data = response.json()
            return payment_data['data'][0]['payment_id']
