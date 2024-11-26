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
import json, requests
import logging
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from odoo.exceptions import AccessError, ValidationError
from odoo import models, fields, _
from odoo.http import request

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    hyperpay_transaction_id = fields.Char(
        string="HyperPay Transaction ID",
        readonly=True,
    )

    hyperpay_transaction_currency = fields.Char(
        string="HyperPay Transaction Currency",
        readonly=True,
    )

    hyperpay_transaction_status = fields.Char(
        string="HyperPay Transaction Status",
        readonly=True,
    )
    hyperpay_payment_type = fields.Char(string='HyperPay Payment Type', readonly=True)

    hyperpay_refund_id = fields.Char(
        string="HyperPay Refund ID",
        readonly=True,
    )
    hyperpay_refund_currency = fields.Char(
        string="HyperPay Refund Currency",
        readonly=True,
    )
    hyperpay_refund_status = fields.Char(
        string="HyperPay Refund Status",
        readonly=True,
    )

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'hyperPay':
            return res
        response = self.send_payment(self.reference)
        return {
            'api_url': response,
            'reference': self.reference
        }

    def send_payment(self, reference):
        hyper_api_url = self.env['payment.provider'].search([('code', '=', 'hyperPay')])._hyperpay_get_api_url()
        url = f"{hyper_api_url}paybylink/v1"
        current_website_name = request.env['website'].sudo().get_current_website().name
        provider = request.env['payment.provider'].search([('code', '=', 'hyperPay')], limit=1)
        partner = self.partner_id
        # Format amount to ensure it has exactly two decimal places
        formatted_amount = f"{self.amount:.2f}"
        base_url = self.provider_id.get_base_url()
        success_url = "payment/hyperPay/redirect"
        data = {
            'entityId': provider.hyperpay_entity_id,
            'amount': formatted_amount,
            'currency': self.currency_id.name,
            'paymentType': 'DB',
            'merchant.name': current_website_name,
            'layout.merchantNameColor': '#ffffff',
            'layout.amountColor': '#ffffff',
            'layout.payButtonColor': '#0dcaf0',
            'layout.payButtonTextColor': '#ffffff',
            'validUntil': '1',
            'validUntilUnit': 'DAY',
            'termsAndConditionsUrl': 'https://mtsTandCs.com',
            'privacyPolicyUrl': 'https://mtsPrivacyPolicy.com',
            'merchantTransactionId': reference,
            'shopperResultUrl': f"{base_url}{success_url}?reference={reference}",
            'customer.givenName': self.partner_id.name.split()[0],
            'customer.surname': self.partner_id.name.split()[-1],
            'customer.mobile': self.partner_id.mobile,
            'customer.email': self.partner_id.email,
            'collectBilling': 'street1,houseNumber1,postcode,city,country',
            'mandatoryBilling': 'street1,houseNumber1,postcode,city,country',
            'billing.street1': partner.street,
            'billing.houseNumber1': '1234',
            'billing.postcode': partner.zip,
            'billing.city': partner.city,
            'billing.country': partner.country_id.code,
            'createQRCode': 'true',
        }

        data_encoded = urlencode(data).encode('utf-8')
        request_obj = Request(url, data=data_encoded)
        request_obj.add_header('Authorization', f'Bearer {provider.authorization_bearer}')
        request_obj.get_method = lambda: 'POST'

        try:
            with urlopen(request_obj) as response:
                response_data = json.loads(response.read().decode())
                _logger.info("Payment response: %s", response_data)
                return response_data.get('link')
        except HTTPError as e:
            error_data = json.loads(e.read().decode())
            _logger.error("HTTPError: %s", error_data)
            return error_data
        except URLError as e:
            _logger.error("URLError: %s", e.reason)
            return {'error': e.reason}
        except Exception as e:
            _logger.error("Unexpected error: %s", e)
            return {'error': str(e)}

    def _get_tx_from_notification_data(self, provider_code, notification_data):

        """Override of payment to find the transaction based on hyperPay data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != "hyperPay" or len(tx) == 1:
            return tx

        reference = notification_data.get("reference")

        tx = self.search(
            [("reference", "=", reference), ("provider_code", "=", "hyperPay")]
        )
        if not tx:
            raise ValidationError(
                "hyperPay: "
                + _("No transaction found matching reference %s.", reference)
            )

        return tx


    def _hyperPay_form_validate(self, data):
        _logger.debug(f"HyperPay response data: {data}")

        pay_id = data.get('id')
        checkout_id = data.get('checkoutId')
        if not checkout_id:
            raise ValidationError("No checkoutId found in the response.")

        provider = self.env['payment.provider'].search([('code', '=', 'hyperPay')], limit=1)
        if not provider:
            raise ValidationError("HyperPay provider not found.")
        hyper_api_url = self.env['payment.provider'].search([('code', '=', 'hyperPay')])._hyperpay_get_api_url()
        url = f"{hyper_api_url}paybylink/v1/{pay_id}/checkouts/{checkout_id}/payment"
        url += f'?entityId={provider.hyperpay_entity_id}'

        try:
            request_obj = Request(url)
            request_obj.add_header('Authorization', f'Bearer {provider.authorization_bearer}')
            response = urlopen(request_obj)
            response_data = json.loads(response.read().decode())
            _logger.debug(f"HyperPay payment validation response: {response_data}")

            self.write({
                "hyperpay_transaction_id": response_data.get('id'),
                "provider_reference": response_data.get('id'),
                "hyperpay_transaction_currency": response_data.get('currency'),
                "hyperpay_payment_type": response_data.get('paymentType'),
                "hyperpay_transaction_status": response_data.get('status'),
            })

            status = response_data['result']['code']
            if status in ["pending", "delayed"]:
                self._set_pending()
            elif status == "000.100.110":
                self._set_done()
                self.write({
                    "hyperpay_transaction_status": "Success",
                })
            else:
                self._set_canceled()
                self.write({
                    "hyperpay_transaction_status": "Failed",
                })

        except HTTPError as e:
            error_data = json.loads(e.read().decode())
            _logger.error(f"HTTPError during HyperPay validation: {error_data}")
            raise ValidationError(f"HTTPError: {error_data}")

        except URLError as e:
            _logger.error(f"URLError during HyperPay validation: {e.reason}")
            raise ValidationError(f"URLError: {e.reason}")

        except Exception as e:
            _logger.error(f"Unexpected error during HyperPay validation: {e}")
            raise ValidationError(f"Unexpected error: {str(e)}")

    def _process_notification_data(self, notification_data):

        """Override of payment to process the transaction based on hyperPay data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        _logger.debug(f"Received notification data:\n{notification_data}")
        super()._process_notification_data(notification_data)
        if self.provider_code != "hyperPay":
            return

        self._hyperPay_form_validate(notification_data)
