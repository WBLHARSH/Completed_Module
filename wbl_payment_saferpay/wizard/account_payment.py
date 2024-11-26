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
from docutils.nodes import header

from odoo import _, api, fields, models
import uuid, requests,base64
from odoo.exceptions import UserError, ValidationError


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
    saferPay_transaction_id = fields.Char(string="saferPay Transaction ID",
                                          related='relation_to.payment_transaction_id.saferPay_transaction_id',
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
        provider = self.env['payment.provider'].search([('code', '=', 'saferPay')], limit=1)
        base_api_url = provider._saferpay_get_api_url()
        url = f"{base_api_url}Payment/v1/Transaction/Refund"
        txn_id = self.saferPay_transaction_id
        capture_id = self.capture_payment(txn_id, provider)
        # Headers for the API request
        headers = self.saferPay_header(provider)
        refund_amount = self.refund_amount
        if refund_amount:
            payload = {
                "RequestHeader": {
                    "SpecVersion": "1.31",
                    "CustomerId": provider.saferPay_customer_id,
                    "RequestId": str(uuid.uuid4()),
                    "RetryIndicator": 0
                },
                "Refund": {
                    "Amount": {
                        "Value": int(refund_amount*100),
                        "CurrencyCode": self.transaction.currency_id.name
                    }
                },
                "CaptureReference": {
                    "CaptureId": capture_id
                }
            }

            response = requests.post(url, headers=headers, json=payload)
            payment_data = response.json()
            print(payment_data)
            if response.status_code == 200:
                payment_data = response.json()
                rfd_id = payment_data['Transaction']['Id']
                status = payment_data['Transaction']['Status']
                if status == 'AUTHORIZED':
                    reference = self.transaction.reference
                    self.env['payment.transaction'].create({
                        'provider_id': provider.id,  # Link to the Paytrail provider
                        'amount': "-" + f"{self.refund_amount}",  # Refund amount
                        'currency_id': self.transaction.currency_id.id,
                        'reference': "R-" + reference,  # New reference with 'R-'
                        'provider_reference': rfd_id,  # Store the refund transaction ID
                        'partner_id': self.transaction.partner_id.id,  # Link to the same partner
                        'state': 'done',  # Mark the transaction as completed
                        'payment_id': self.transaction.payment_id.id,  # Link to the original payment ID
                        'payment_method_id': self.transaction.payment_method_id.id,
                        'saferPay_refund_id': rfd_id,
                        'saferPay_refund_currency': self.transaction.currency_id.name,
                        'saferPay_refund_status': status,
                        'saferPay_transaction_type': 'REFUND'
                    })
                else:
                    payment_data = response.json()
                    raise ValidationError(f"Refund failed: {payment_data['ErrorMessage']}")
            else:
                payment_data = response.json()
                raise ValidationError(f"Refund failed: {payment_data['ErrorMessage']}")
        else:
            raise ValidationError(f"Refund failed: Refund Amount Not Found or Refund Reason Not Found")

    def capture_payment(self, txn_id, provider):
        base_api_url = provider._saferpay_get_api_url()
        url = f"{base_api_url}Payment/v1/Transaction/Capture"
        headers = self.saferPay_header(provider)
        payload = {
            "RequestHeader": {
                "SpecVersion": "1.31",
                "CustomerId": provider.saferPay_customer_id,
                "RequestId": str(uuid.uuid4()),
                "RetryIndicator": 0
            },
            "TransactionReference": {
                "TransactionId": txn_id
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        payment_data = response.json()
        print(payment_data)
        return payment_data['CaptureId']

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