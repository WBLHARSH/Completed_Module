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
    amount = fields.Monetary(
        string="Payment Amount",
        related='relation_to.amount',
        currency_field='currency_id',
        readonly=True
    )
    transaction = fields.Many2one(string="Transaction ID",
                                  related='relation_to.payment_transaction_id',
                                  readonly=True)
    klarna_transaction_id = fields.Char(string="Klarna Transaction ID",
                                        related='relation_to.payment_transaction_id.klarna_transaction_id',
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
        base_api_url = self.env['payment.provider'].search([('code', '=', 'klarna')], limit=1)._klarna_get_api_url()
        api_url = f"{base_api_url}ordermanagement/v1/orders/cab8b20d-83f4-477c-9638-8661bc173296/refunds"
        api_key = self.env['payment.provider'].search([('code', '=', 'klarna')])

        klarna_username = api_key.klarna_username
        klarna_password = api_key.klarna_password
        # Headers for the API request
        headers = {
            'Content-Type': 'application/json',
        }
        refund_amount = self.refund_amount
        refund_reason = self.refund_reason
        if refund_amount and refund_reason:
            payload = {
                "refunded_amount": self.refund_amount,
                "description": self.refund_reason
            }

            response = requests.post(api_url, auth=HTTPBasicAuth(klarna_username, klarna_password), headers=headers,
                                     json=payload)
            if response.status_code == 201:
                payment_data = response.json()
                print('payment_data', payment_data)

            else:
                payment_data = response.json()
                print('fail payment_data', payment_data)
        else:
            raise ValidationError(f"Refund failed: Refund Amount Not Found or Refund Reason Not Found")
