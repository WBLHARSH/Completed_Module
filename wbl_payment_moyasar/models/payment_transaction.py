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
from odoo.exceptions import AccessError, ValidationError, UserError
import requests
from requests.auth import HTTPBasicAuth

from odoo import models, fields, _

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    """Inherited class of payment transaction to add moyasar functions."""
    _inherit = 'payment.transaction'

    moyasar_transaction_id = fields.Char(
        string="Moyasar Transaction ID",
        readonly=True,
    )

    moyasar_transaction_currency = fields.Char(
        string="Moyasar Transaction Currency",
        readonly=True,
    )

    moyasar_transaction_status = fields.Char(
        string="Moyasar Transaction Status",
        readonly=True,
    )
    moyasar_transaction_type = fields.Char(string='moyasar Payment Type', readonly=True)

    moyasar_refund_id = fields.Char(
        string="Moyasar Refund ID",
        readonly=True,
    )
    moyasar_refund_currency = fields.Char(
        string="Moyasar Refund Currency",
        readonly=True,
    )
    moyasar_refund_status = fields.Char(
        string="Moyasar Refund Status",
        readonly=True,
    )

    def _get_specific_rendering_values(self, processing_values):
        """ Function to fetch the values of the payment gateway"""
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'moyasar':
            return res
        return self.send_payment()

    def send_payment(self):
        """Send payment information to Klarna for processing."""
        odoo_base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        return {
            'api_url': f"{odoo_base_url}/payment/moyasar/response",
            "publishable_api_key": self.provider_id.moyasar_public_key,
            "currency": self.currency_id.name,
            "amount": (self.amount) * 100,
            "description": self.reference,
            "callback_url": f"{odoo_base_url}/payment/moyasar/redirect?reference={self.reference}",
        }

    def _get_tx_from_notification_data(self, provider_code, notification_data):

        """Override of payment to find the transaction based on moyasar data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != "moyasar" or len(tx) == 1:
            return tx

        reference = notification_data.get("reference")
        tx = self.search(
            [("reference", "=", reference), ("provider_code", "=", "moyasar")]
        )
        if not tx:
            raise ValidationError(
                "moyasar: "
                + _("No transaction found matching reference %s.", reference)
            )

        return tx

    def _moyasar_form_validate(self, data):
        _logger.debug(f"moyasar response data: {data}")
        try:
            res = {
                "moyasar_transaction_id": data.get('id'),
                "provider_reference": data.get('id'),
                "moyasar_transaction_currency": self.currency_id.name,
                "moyasar_transaction_status": data['message'],
                "moyasar_transaction_type": 'PAYMENT',
            }
            self.write(res)

            moyasar_status = data['message']
            if moyasar_status in ["pending", "delayed"]:
                self._set_pending()
            elif moyasar_status == "APPROVED":
                self._set_done()
            else:
                self._set_canceled()

        except requests.RequestException as e:
            _logger.error(f"Error in moyasar API request: {e}")
            self._set_canceled()

        except Exception as e:
            _logger.error(f"Error during moyasar validation: {e}")
            self._set_canceled()

    def _process_notification_data(self, notification_data):

        """Override of payment to process the transaction based on moyasar data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        _logger.debug(f"Received notification data:\n{notification_data}")
        super()._process_notification_data(notification_data)
        if self.provider_code != "moyasar":
            return

        self._moyasar_form_validate(notification_data)

    # def _get_specific_processing_values(self, processing_values):
    #     res = super()._get_specific_processing_values(processing_values)
    #     if self.provider_code != 'moyasar':
    #         return res
    #
    #     if self.operation in ('online_token', 'offline'):
    #         return {}
    #     return {
    #         'moyasar_public_key': self.provider_id.moyasar_public_key,
    #     }
