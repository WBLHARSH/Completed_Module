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
import uuid,requests
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
    airwallex_transaction_id = fields.Char(string="airwallex Transaction ID",
                                           related='relation_to.payment_transaction_id.airwallex_transaction_id',
                                           readonly=True)
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
        provider = self.env['payment.provider'].search([('code', '=', 'airwallex')], limit=1)
        bearerToken = provider.bearerToken()
        if bearerToken:
            url = "https://api-demo.airwallex.com/api/v1/pa/refunds/create"

            # Headers for the API request
            headers = {
                "Authorization": f"Bearer {bearerToken}",
                'Content-Type': 'application/json'
            }
            refund_amount = self.refund_amount
            refund_reason = self.refund_reason
            if refund_amount and refund_reason:
                payload = {
                    "amount": refund_amount,
                    "payment_attempt_id": self.transaction.airwallex_attempt_id,
                    "payment_intent_id": self.transaction.airwallex_transaction_id,
                    "reason": refund_reason,
                    "request_id": str(uuid.uuid4()),
                }

                response = requests.post(url, headers=headers, json=payload)
                if response.status_code == 201:
                    payment_data = response.json()
                    rfd_id = payment_data['id']
                    status = payment_data['status']
                    if status:
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
                        })
                else:
                    payment_data = response.json()
                    raise ValidationError(f"Refund failed: {payment_data['message']}")
            else:
                raise ValidationError(f"Refund failed: Refund Amount Not Found or Refund Reason Not Found")
        else:
            raise ValidationError(f"Refund failed: Bearer Token Not Found")
