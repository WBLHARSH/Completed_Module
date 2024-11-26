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


from odoo import _, api, fields, models
import uuid, requests
from odoo.exceptions import UserError, ValidationError
from requests.auth import HTTPBasicAuth


class RefundAmount(models.TransientModel):
    _name = 'refund.amount.wizard'

    relation_to = fields.Many2one(comodel_name='account.payment', required=True)
    refund_amount = fields.Monetary(
        string="Payment Amount",
        related='relation_to.amount',
        currency_field='currency_id',
        readonly=True
    )
    transaction = fields.Many2one(string="Transaction ID",
                                  related='relation_to.payment_transaction_id',
                                  readonly=True)
    moyasar_transaction_id = fields.Char(string="Moyasar Transaction ID",
                                         related='relation_to.payment_transaction_id.moyasar_transaction_id',
                                         readonly=True)

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
        provider = self.env['payment.provider'].search([('code', '=', 'moyasar')], limit=1)
        url = f"https://api.moyasar.com/v1/payments/{self.moyasar_transaction_id}/refund"
        username = provider.moyasar_secret_key
        password = ''
        # Headers for the API request
        headers = {
            'content-type': 'application/json'
        }
        refund_amount = int(self.refund_amount * 100)
        if refund_amount:
            payload = {
                'amount': refund_amount
            }

            response = requests.post(url, auth=HTTPBasicAuth(username, password), headers=headers,
                                     json=payload)
            if response.status_code == 200:
                payment_data = response.json()
                rfd_id = payment_data['id']
                status = payment_data['status']
                if status == 'refunded':
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
                        'moyasar_transaction_type': "REFUND",
                        'moyasar_refund_id': rfd_id,
                        'moyasar_refund_currency': payment_data['currency'],
                        'moyasar_refund_status': payment_data['status'],
                    })
                else:
                    payment_data = response.json()
                    raise ValidationError(f"Refund failed: {payment_data['message']}")
            else:
                payment_data = response.json()
                raise ValidationError(f"Refund failed: {payment_data['message']}")
        else:
            raise ValidationError(f"Refund failed: Refund Amount Not Found")
