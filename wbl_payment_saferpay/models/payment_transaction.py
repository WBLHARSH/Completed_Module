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
import requests, uuid, base64
from odoo.exceptions import UserError, ValidationError
import logging
from werkzeug import urls
from odoo.http import request

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    saferPay_transaction_id = fields.Char(
        string="SaferPay Transaction ID",
        readonly=True,
    )
    saferPay_token = fields.Char(
        string="SaferPay Token",
        readonly=True,
    )

    saferPay_transaction_currency = fields.Char(
        string="SaferPay Transaction Currency",
        readonly=True,
    )

    saferPay_transaction_status = fields.Char(
        string="SaferPay Transaction Status",
        readonly=True,
    )

    saferPay_payment_id = fields.Char(
        string="SaferPay Payment Id",
        readonly=True,
    )

    saferPay_transaction_type = fields.Char(string='saferPay Payment Type', readonly=True)

    saferPay_refund_id = fields.Char(
        string="SaferPay Refund ID",
        readonly=True,
    )
    saferPay_refund_currency = fields.Char(
        string="SaferPay Refund Currency",
        readonly=True,
    )
    saferPay_refund_status = fields.Char(
        string="SaferPay Refund Status",
        readonly=True,
    )

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)

        if self.provider_code != 'saferPay':
            return res
        response = self.send_payment()
        return response

    def send_payment(self):
        print('Workinf')
        provider = self.env['payment.provider'].search([('code', '=', 'saferPay')], limit=1)
        base_api_url = provider._saferpay_get_api_url()
        if not provider:
            raise UserError(_("Payment provider for saferPay not found."))
        print('it"s')
        url = f"{base_api_url}Payment/v1/PaymentPage/Initialize"
        headers = self.saferPay_header(provider)
        base_url = self.provider_id.get_base_url()

        payload = {
            "RequestHeader": {
                "SpecVersion": "1.31",
                "CustomerId": provider.saferPay_customer_id,
                "RequestId": str(uuid.uuid4()),
                "RetryIndicator": 0
            },
            "TerminalId": provider.saferPay_terminal_id,
            "Payment": {
                "Amount": {
                    "Value": int(self.amount * 100),
                    "CurrencyCode": self.currency_id.name
                },
                "OrderId": self.reference,
                "Description": f"Payment for Order {self.reference} by {self.partner_id.name}"
            },
            "ReturnUrls": {
                "Success": f"{base_url}payment/saferpay/success?reference={self.reference}",
                "Fail": f"{base_url}payment/saferpay/fail?reference={self.reference}",
                "Abort": f"{base_url}payment/saferpay/fail?reference={self.reference}"
            },
            "Condition": "WITH_LIABILITY_SHIFT"
        }
        print(url, headers, payload)
        response = requests.post(url, json=payload, headers=headers)
        print(response.json())
        if response.status_code == 200:
            response_json = response.json()
            token = response_json['Token']
            self.saferPay_token = token
            return {
                'api_url': response_json['RedirectUrl'],
            }
        else:
            raise Exception(f"Payment failed: {response.status_code} - {response.text}")

    def base64_user_and_pass(self, credential):
        if credential:
            return base64.b64encode(credential.encode()).decode()

    def saferPay_header(self, provider):
        if provider.saferPay_username and provider.saferPay_password:
            credential = f"{provider.saferPay_username}:{provider.saferPay_password}"
            authentication = self.base64_user_and_pass(credential)
            header_data = {
                'Content-Type': "application/json; charset=utf-8",
                'Accept': "application/json",
                'Authorization': f"Basic {authentication}",
            }
            return header_data
        raise UserError(_('Something Went wrong in username and password.'))

    def _get_tx_from_notification_data(self, provider_code, notification_data):

        """Override of payment to find the transaction based on saferPay data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != "saferPay" or len(tx) == 1:
            return tx

        reference = notification_data.get("reference")
        tx = self.search(
            [("reference", "=", reference), ("provider_code", "=", "saferPay")]
        )
        if not tx:
            raise ValidationError(
                "saferPay: "
                + _("No transaction found matching reference %s.", reference)
            )

        return tx

    def _saferPay_form_validate(self, data):
        _logger.debug(f"saferPay response data: {data}")

        try:
            # Fetch the payment provider configuration
            provider = self.env['payment.provider'].search([('code', '=', 'saferPay')], limit=1)
            base_api_url = provider._saferpay_get_api_url()
            if not provider:
                raise ValueError("saferPay provider not found.")

            # Fetch additional data from saferPay API using payment_intent_id
            _logger.info(f"Transaction ID: {self.saferPay_transaction_id}")

            api_url = f"{base_api_url}Payment/v1/PaymentPage/Assert"
            print(api_url)
            headers = self.saferPay_header(provider)
            print(headers)
            payload = {
                "RequestHeader": {
                    "SpecVersion": "1.31",
                    "CustomerId": provider.saferPay_customer_id,
                    "RequestId": str(uuid.uuid4()),
                    "RetryIndicator": 0
                },
                "Token": self.saferPay_token
            }
            response = requests.post(api_url, json=payload, headers=headers)
            payment_data = response.json()
            print(payment_data)
            _logger.debug(f"saferPay API response: {payment_data}")
            if payment_data:
                saferPay_status = payment_data['Transaction']['Status']
                if saferPay_status in ["pending", "delayed"]:
                    self._set_pending()
                elif saferPay_status == "AUTHORIZED":
                    self._set_done()
                    res = {
                        "saferPay_transaction_id": payment_data['Transaction']['Id'],
                        "provider_reference": payment_data['Transaction']['Id'],
                        "saferPay_transaction_currency": payment_data['Transaction']['Amount']['CurrencyCode'],
                        "saferPay_transaction_status": saferPay_status,
                        'saferPay_transaction_type': 'PAYMENT',
                    }
                    self.write(res)
                else:
                    self._set_canceled()
                    res = {
                        "provider_reference": payment_data['Transaction']['Id'],
                        "saferPay_transaction_currency": payment_data['Transaction']['Amount']['CurrencyCode'],
                        "saferPay_transaction_status": "Cancel",
                    }
                    self.write(res)
            else:
                _logger.error("Transaction ID mismatch.")
                self._set_canceled()

        except requests.RequestException as e:
            _logger.error(f"Error in saferPay API request: {e}")
            self._set_canceled()

        except Exception as e:
            _logger.error(f"Error during saferPay validation: {e}")
            self._set_canceled()

    def _process_notification_data(self, notification_data):

        """Override of payment to process the transaction based on saferPay data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        _logger.debug(f"Received notification data:\n{notification_data}")
        super()._process_notification_data(notification_data)
        if self.provider_code != "saferPay":
            return

        self._saferPay_form_validate(notification_data)
