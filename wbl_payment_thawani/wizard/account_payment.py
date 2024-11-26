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
    thawani_transaction_id = fields.Char(string="Thawani Transaction ID",
                                         related='relation_to.payment_transaction_id.thawani_transaction_id',
                                         readonly=True)
    thawani_payment_id = fields.Char(string="Thawani Payment ID",
                                     related='relation_to.payment_transaction_id.thawani_payment_id', readonly=True)
    refund_reason = fields.Char(string="Refund Reason", size=125, required=True)
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
        provider = self.env['payment.provider'].search([('code', '=', 'thawani')], limit=1)
        base_api_url = provider._thawani_get_api_url()
        url = f"{base_api_url}api/v1/refunds"

        # Headers for the API request
        headers = {
            'Content-Type': "application/json",
            'Accept': "application/json",
            'thawani-api-key': provider.thawani_secret_key
        }
        refund_amount = self.refund_amount
        refund_reason = self.refund_reason
        if refund_reason:
            payload = {
                "payment_id": self.thawani_payment_id,
                "reason": refund_reason,
                "metadata": {
                    "customer": self.transaction.partner_id.name
                },
                'amount': int(self.amount * 1000)
            }

            response = requests.post(url, headers=headers, json=payload)
            payment_data = response.json()
            if response.status_code == 200:
                payment_data = response.json()
                rfd_id = payment_data['data']['refund_id']
                status = payment_data['data']['status']
                if status == 'successful':
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
                        'thawani_refund_id':rfd_id,
                        'thawani_refund_currency':self.transaction.currency_id.name,
                        'thawani_refund_status':status,
                        'thawani_transaction_type':'REFUND'
                    })
                else:
                    payment_data = response.json()
                    raise ValidationError(f"Refund failed: {payment_data['description']}")
            else:
                payment_data = response.json()
                raise ValidationError(f"Refund failed: {payment_data['description']}")
        else:
            raise ValidationError(f"Refund failed: Refund Amount Not Found or Refund Reason Not Found")
