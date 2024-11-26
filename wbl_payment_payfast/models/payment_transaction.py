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

# Import required libraries (make sure it is installed!)
import logging
import hashlib
import urllib.parse
from odoo import models, fields, _
import uuid
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError, UserError
import requests

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    """Inherited class of payment transaction to add payfast functions."""
    _inherit = 'payment.transaction'

    payfast_transaction_id = fields.Char(
        string="Payfast Transaction ID",
        readonly=True,
    )

    payfast_transaction_currency = fields.Char(
        string="Payfast Transaction Currency",
        readonly=True,
    )

    payfast_transaction_status = fields.Char(
        string="Payfast Transaction Status",
        readonly=True,
    )

    def _get_specific_rendering_values(self, processing_values):
        """ Function to fetch the values of the payment gateway"""
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'payfast':
            return res
        return self.send_payment()

    def send_payment(self):
        """Send payment information to Payfast for processing."""
        payfast_api_url = self.env['payment.provider'].search([('code', '=', 'payfast')])._payfast_get_api_url()
        provider = request.env['payment.provider'].search([('code', '=', 'payfast')], limit=1)
        formatted_amount = f"{self.amount:.2f}"
        odoo_base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        success_url = "/payment/payfast/redirect"
        cancel_url = "/payment/payfast/cancel"
        notify_url = "/payment/payfast/notify"
        data = {
            # Merchant details
            'merchant_id': f'{provider.payfast_merchant_id}',
            'merchant_key': f'{provider.payfast_merchant_key}',
            'return_url': f"{odoo_base_url}{success_url}?reference={self.reference}",
            'cancel_url': f"{odoo_base_url}{cancel_url}?reference={self.reference}",
            'notify_url': f"{odoo_base_url}{notify_url}?reference={self.reference}",
            # Buyer details
            'name_first': self.partner_id.name.split()[0],
            'name_last': self.partner_id.name.split()[-1],
            'email_address': self.partner_id.email,
            # Transaction details
            'm_payment_id': self.reference,  # Unique payment ID to pass through to notify_url
            'amount': formatted_amount,
            'item_name': self.reference
        }

        # Generate the signature
        passphase = f'{provider.payfast_passphrase}'
        signature = self.generateSignature(data, passphase)
        return {
            # Merchant details
            'api_url': payfast_api_url,
            'merchant_id': f'{provider.payfast_merchant_id}',
            'merchant_key': f'{provider.payfast_merchant_key}',
            'return_url': f"{odoo_base_url}{success_url}?reference={self.reference}",
            'cancel_url': f"{odoo_base_url}{cancel_url}?reference={self.reference}",
            'notify_url': f"{odoo_base_url}{notify_url}?reference={self.reference}",
            # Buyer details
            'name_first': self.partner_id.name.split()[0],
            'name_last': self.partner_id.name.split()[-1],
            'email_address': self.partner_id.email,
            # Transaction details
            'm_payment_id': self.reference,  # Unique payment ID to pass through to notify_url
            'amount': formatted_amount,
            'item_name': self.reference,
            'signature': signature
        }

    def generateSignature(self, dataArray, passPhrase=''):
        payload = ""
        for key in dataArray:
            # Get all the data from Payfast and prepare parameter string
            payload += key + "=" + urllib.parse.quote_plus(dataArray[key].replace("+", " ")) + "&"
        # After looping through, cut the last & or append your passphrase
        payload = payload[:-1]
        if passPhrase != '':
            payload += f"&passphrase={passPhrase}"
        return hashlib.md5(payload.encode()).hexdigest()

    def _get_tx_from_notification_data(self, provider_code, notification_data):

        """Override of payment to find the transaction based on payfast data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != "payfast" or len(tx) == 1:
            return tx

        reference = notification_data.get("reference")
        tx = self.search(
            [("reference", "=", reference), ("provider_code", "=", "payfast")]
        )
        if not tx:
            raise ValidationError(
                "payfast: "
                + _("No transaction found matching reference %s.", reference)
            )

        return tx

    def _payfast_form_validate(self, data):
        _logger.debug(f"payfast response data: {data}")
        try:
            res = {
                "payfast_transaction_id": data.get('pf_payment_id'),
                "provider_reference": data.get('pf_payment_id'),
                "payfast_transaction_status": data['payment_status'],
            }
            self.write(res)

            payfast_status = data['payment_status']
            if payfast_status in ["pending", "delayed"]:
                self._set_pending()
            elif payfast_status == "COMPLETE" or self.payfast_transaction_status == 'COMPLETE':
                self._set_done()
            else:
                self._set_canceled()

        except requests.RequestException as e:
            _logger.error(f"Error in payfast API request: {e}")
            self._set_canceled()

        except Exception as e:
            _logger.error(f"Error during payfast validation: {e}")
            self._set_canceled()

    def _process_notification_data(self, notification_data):

        """Override of payment to process the transaction based on payfast data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        _logger.debug(f"Received notification data:\n{notification_data}")
        super()._process_notification_data(notification_data)
        if self.provider_code != "payfast":
            return

        self._payfast_form_validate(notification_data)
