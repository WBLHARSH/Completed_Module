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

from odoo import models, fields, _
import logging,requests
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    airwallex_transaction_id = fields.Char(string='Transaction ID', help='Airwallex payment transaction id')
    airwallex_attempt_id = fields.Char(string='Attempt ID', help='Airwallex payment attempt id')
    airwallex_payment_currency = fields.Char(string='Transaction Currency',
                                             help='Airwallex payment transaction currency')
    airwallex_payment_status = fields.Char(string='Transaction Status', help='Airwallex payment transaction status')

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'airwallex' or len(tx) == 1:
            return tx

        reference = notification_data.get('reference')
        if not reference:
            raise ValidationError("No reference found in notification data.")

        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'airwallex')])
        if not tx:
            raise ValidationError(_("No transaction found matching reference %s.", reference))
        return tx

    def _airwallex_form_validate(self, data):
        _logger.debug(f"Airwallex response data: {data}")
        payment_intent_id = data.get('id')
        provider = self.env['payment.provider'].search([('code', '=', 'airwallex')], limit=1)
        bearerToken = provider.bearerToken()

        if not payment_intent_id:
            raise ValidationError("No payment_intent_id found in the response.")

        # Fetch additional data from Airwallex API using payment_intent_id
        api_url = f"https://api-demo.airwallex.com/api/v1/pa/payment_intents/{payment_intent_id}"
        headers = {
            "Authorization": f"Bearer {bearerToken}",
            "Content-Type": "application/json"
        }

        response = requests.get(api_url, headers=headers)

        if response.status_code != 200:
            raise ValidationError(f"Failed to retrieve data from Airwallex: {response.text}")

        payment_data = response.json()

        res = {
            "airwallex_transaction_id": payment_data.get('id'),
            "airwallex_attempt_id": payment_data['latest_payment_attempt']['id'],
            "provider_reference": payment_data.get('id'),
            "airwallex_payment_currency": payment_data.get('currency'),
            "airwallex_payment_status": payment_data.get('status'),
        }
        self.write(res)
        airwallex_status = payment_data.get('status')
        if airwallex_status in ["pending", "delayed"]:
            _logger.info(_("Airwallex payment for tx %s: set as pending", self.reference))
            self._set_pending()
        elif airwallex_status == "SUCCEEDED":
            _logger.info(_("Airwallex payment for tx %s: set as done", self.reference))
            self._set_done()
        else:
            _logger.info(_("Airwallex payment for tx %s: set as canceled", self.reference))
            self._set_canceled()


    def _process_notification_data(self, notification_data):
        _logger.debug(f"Received notification data:\n{notification_data}")
        super()._process_notification_data(notification_data)
        if self.provider_code != "airwallex":
            return

        self._airwallex_form_validate(notification_data)
