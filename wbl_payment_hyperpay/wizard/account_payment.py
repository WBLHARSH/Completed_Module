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
from urllib.parse import urlencode
from urllib.request import build_opener, Request, HTTPHandler
from urllib.error import HTTPError, URLError
import json
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class RefundAmount(models.TransientModel):
    _name = 'refund.amount.wizard'

    relation_to = fields.Many2one(comodel_name='account.payment', required=True)
    amount = fields.Monetary(
        string="Payment Amount",
        related='relation_to.amount',
        currency_field='currency_id',
        readonly=True
    )
    transaction = fields.Many2one(string="Transaction ID",
                                  related='relation_to.payment_transaction_id',
                                  readonly=True)
    hyperpay_transaction_id = fields.Char(string="HyperPay Transaction ID",
                                          related='relation_to.payment_transaction_id.hyperpay_transaction_id',
                                          readonly=True)
    maximum_refund = fields.Monetary(
        string="Maximum Refund Amount",
        related='relation_to.amount',
        currency_field='currency_id',
        readonly=True
    )
    refund_amount = fields.Monetary(
        string="Refund Amount",
        required=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        compute='_compute_currency_id',
        store=True,
        readonly=False
    )

    @api.model
    def default_get(self, fields_list):
        res = super(RefundAmount, self).default_get(fields_list)
        # Check if context has a specific payment id to set
        if self._context.get('active_id'):
            res['relation_to'] = self._context.get('active_id')
        return res

    @api.depends('relation_to')
    def _compute_currency_id(self):
        for record in self:
            record.currency_id = record.relation_to.currency_id

    def action_send_refund(self):
        payment_method_code = self.transaction.payment_method_id.code
        hyper_api_url = self.env['payment.provider'].search([('code', '=', 'hyperpay')])._hyperpay_get_api_url()
        url = f"{hyper_api_url}v1/payments/{self.hyperpay_transaction_id}"
        provider = self.env['payment.provider'].search([('code', '=', 'hyperpay')], limit=1)
        print(provider.journal_id)
        if payment_method_code == 'mada':
            entity_id = provider.hyperpay_merchant_id_mada
        else:
            entity_id = provider.hyperpay_merchant_id

        data = {
            'entityId': entity_id,
            'amount': "{:.2f}".format(self.refund_amount),  # Ensure the amount has 2 decimal places
            'paymentType': 'RF',
            'currency': self.currency_id.name  # Dynamically pass currency
        }

        headers = {
            'Authorization': f'Bearer {provider.hyperpay_authorization_bearer}'
        }

        try:
            opener = build_opener(HTTPHandler)
            request = Request(url.format(id=self.hyperpay_transaction_id), data=urlencode(data).encode('utf-8'))
            for key, value in headers.items():
                request.add_header(key, value)
            request.get_method = lambda: 'POST'
            response = opener.open(request)
            payment_data = json.loads(response.read())
            if response.status == 200:
                rfd_id = payment_data['id']
                payment_type = payment_data['paymentType']
                rfd_currency = payment_data['currency']
                rfd_refund_status = payment_data['result']['description']
                status = payment_data['result']['code']
                if status == '000.100.110':
                    reference = self.transaction.reference
                    unique_ref = f"R-{reference}-{fields.Datetime.now().strftime('%Y%m%d%H%M%S')}"
                    new_transaction = self.env['payment.transaction'].create({
                        'provider_id': provider.id,  # Link to the Paytrail provider
                        'amount': "-" + f"{self.refund_amount}",  # Refund amount
                        'currency_id': self.transaction.currency_id.id,
                        'reference': unique_ref,  # New reference with 'R-'
                        'provider_reference': rfd_id,  # Store the refund transaction ID
                        'hyperpay_refund_id': rfd_id,  # Store the refund transaction ID
                        'hyperpay_payment_type': payment_type,  # Store the refund transaction ID
                        'hyperpay_refund_currency': rfd_currency,  # Store the refund transaction ID
                        'hyperpay_refund_status': rfd_refund_status,  # Store the refund transaction ID
                        'partner_id': self.transaction.partner_id.id,  # Link to the same partner
                        'state': 'done',  # Mark the transaction as completed
                        'payment_method_id': self.transaction.payment_method_id.id,
                    })
                    new_payment = self.env['account.payment'].create({
                        'amount': self.refund_amount,
                        'currency_id': self.transaction.currency_id.id,
                        'partner_id': self.transaction.partner_id.id,
                        'payment_type': 'outbound',
                        'journal_id': provider.journal_id.id,
                        'payment_method_line_id': self.transaction.payment_id.payment_method_line_id.id,
                        'ref': f"{reference}-{self.transaction.partner_id.name}-{rfd_id}",
                        'payment_transaction_id': new_transaction.id,
                        'hypepay_payment_type': "RF"
                    })
                    new_transaction.write({
                        'payment_id': new_payment.id
                    })
                    new_payment.action_post()
        except HTTPError as e:
            payment_data = json.loads(e.read())
            raise ValidationError(f"Refund failed: {payment_data['result']['description']}")
        except URLError as e:
            raise UserError(_('Error during refund request: %s') % e.reason)
