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
import re
import logging
from werkzeug import urls

import odoo.exceptions
from odoo import api, models, _, fields
from odoo.tools import format_amount
from odoo.exceptions import ValidationError
from odoo.addons.payment import utils as payment_utils
from odoo.addons.wbl_payment_hyperpay import hyperpay_utils as hyperpay

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
    hyperpay_payment_type = fields.Selection([('DB', 'DB'), ('RF', 'RF')], string='HyperPay Payment Type')

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
        if self.provider_code != 'hyperpay':
            return res
        response = self.send_payment()
        return response

    def send_payment(self):
        hyperpay_provider = self.provider_id
        payment_method_code = self.payment_method_id.code

        if payment_method_code == 'mada':
            entity_id = hyperpay_provider.hyperpay_merchant_id_mada
        else:
            entity_id = hyperpay_provider.hyperpay_merchant_id
        if not entity_id:
            raise ValidationError("No entityID provided for '%s' transactions." % payment_method_code)

        request_values = {
            'entityId': '%s' % entity_id,
            'amount': "{:.2f}".format(self.amount),
            'currency': self.currency_id.name,
            'paymentType': 'DB',
            'merchantTransactionId': str(self.reference),
        }
        response_content = self.provider_id._hyperpay_make_checkout_request(request_values)
        response_content['api_url'] = '/payment/hyperpay'
        response_content['checkout_id'] = response_content.get('id')
        response_content['merchantTransactionId'] = self.reference
        response_content['formatted_amount'] = format_amount(self.env, self.amount, self.currency_id)
        response_content['paymentMethodCode'] = payment_method_code
        if hyperpay_provider.state == 'enabled':
            payment_url = "https://eu-prod.oppwa.com/v1/paymentWidgets.js?checkoutId=%s" % response_content[
                'checkout_id']
        else:
            payment_url = "https://eu-test.oppwa.com/v1/paymentWidgets.js?checkoutId=%s" % response_content[
                'checkout_id']
        response_content['payment_url'] = payment_url
        return response_content

    def _get_tx_from_notification_data(self, provider_code, data):
        tx = super()._get_tx_from_notification_data(provider_code, data)
        if provider_code not in ('hyperpay', 'mada'):
            return tx
        provider = self.env['payment.provider'].search([('code', '=', 'hyperpay')], limit=1)
        payment_status_url = provider._hyperpay_get_api_url() + data.get('resourcePath')

        notification_data = provider._hyperpay_get_payment_checkout_status(payment_status_url, provider_code)
        reference = notification_data.get('merchantTransactionId', False)
        if not reference:
            raise ValidationError(_("HyperPay: No reference found."))
        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'hyperpay')])
        if not tx:
            raise ValidationError(_("HyperPay: No transaction found matching reference %s.") % reference)
        tx._handle_hyperpay_payment_status(notification_data)
        return tx

    def _handle_hyperpay_payment_status(self, notification_data):
        tx_status_set = False
        status = notification_data.get('result', False)
        if 'id' in notification_data:
            self.provider_reference = notification_data.get('id', False)
        self.write({
            "hyperpay_transaction_id": notification_data.get('id'),
            "provider_reference": notification_data.get('id'),
            "hyperpay_transaction_currency": notification_data.get('currency'),
            "hyperpay_payment_type": notification_data.get('paymentType'),
        })
        if status and 'code' in status:
            status_code = status.get('code')
            if not tx_status_set:
                for reg_exp in hyperpay.PAYMENT_STATUS_CODES_REGEX['SUCCESS']:
                    if re.search(reg_exp, status_code):
                        self._set_done()
                        self.write({
                            "hyperpay_transaction_status": "Success",
                        })
                        tx_status_set = True
                        break

            if not tx_status_set:
                for reg_exp in hyperpay.PAYMENT_STATUS_CODES_REGEX['SUCCESS_REVIEW']:
                    if re.search(reg_exp, status_code):
                        self._set_pending()
                        self.write({
                            "hyperpay_transaction_status": "Success Review",
                        })
                        tx_status_set = True
                        break

            if not tx_status_set:
                for reg_exp in hyperpay.PAYMENT_STATUS_CODES_REGEX['PENDING']:
                    if re.search(reg_exp, status_code):
                        self._set_error()
                        self.write({
                            "hyperpay_transaction_status": "Pending",
                        })
                        tx_status_set = True
                        break

            if not tx_status_set:
                for reg_exp in hyperpay.PAYMENT_STATUS_CODES_REGEX['WAITING']:
                    if re.search(reg_exp, status_code):
                        self._set_error()
                        self.write({
                            "hyperpay_transaction_status": "Waiting",
                        })
                        tx_status_set = True
                        break

            if not tx_status_set:
                for reg_exp in hyperpay.PAYMENT_STATUS_CODES_REGEX['REJECTED']:
                    if re.search(reg_exp, status_code):
                        self._set_error()
                        self.write({
                            "hyperpay_transaction_status": "Rejected",
                        })
                        tx_status_set = True
                        break

            if not tx_status_set:
                _logger.warning("Received unrecognized payment state %s for "
                                "transaction with reference %s\nDetailed Message:%s", status_code, self.reference,
                                status.get('description'))
                self._set_error("HyperPay: " + _("Invalid payment status."))
