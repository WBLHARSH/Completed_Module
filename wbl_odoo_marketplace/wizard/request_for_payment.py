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

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.http import request

class RequestForPaymentWizard(models.TransientModel):
    _name = 'request.payment.wizard'

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)
    cashable_amount = fields.Monetary(string="Cashable Amount", currency_field='currency_id')
    requested_amount = fields.Monetary(string="Requested Payment Amount", currency_field='currency_id', required=True)
    payment_description = fields.Text(string="Payment Description", required=True)

    @api.model
    def default_get(self, fields_list):
        res = super(RequestForPaymentWizard, self).default_get(fields_list)
        # Calculate the total admin commission for the logged-in user's seller
        seller_id = self.env.user.partner_id.seller_id.id
        if seller_id:
            total_credit = sum(self.env['marketplace.seller.payment'].search([
                ('seller_id', '=', seller_id),
                ('payment_type', '=', 'credit'),
                ('state', '=', 'approved'),
            ]).mapped('payment_amount'))

            total_debit = sum(self.env['marketplace.seller.payment'].search([
                ('seller_id', '=', seller_id),
                ('payment_type', '=', 'debit'),
                ('state', '=', 'approved'),
            ]).mapped('payment_amount'))
            res['cashable_amount'] = total_credit - total_debit
        return res

    def action_payment_request(self):
        # Ensure the requested amount is not greater than the cashable amount
        settings = request.env['res.config.settings'].sudo().get_values()
        if self.cashable_amount > 0.0 and self.requested_amount > 0.0:
            if self.requested_amount > self.cashable_amount:
                raise UserError(_("The requested amount exceeds the available cashable amount."))
        else:
            raise UserError(_("Cashable amount and requested amount must be greater than zero."))

        # Create a record in the marketplace.seller.payment model
        seller_payment = self.env['marketplace.seller.payment'].create({
            'seller_payment_reference': self.env['ir.sequence'].next_by_code('marketplace.seller.payment') or '/',
            'user_id': self.env.user.id,
            'seller_id': self.env.user.partner_id.seller_id.id,  # Assuming seller_id is related to partner_id
            'currency_id': self.currency_id.id,
            'payment_amount': self.requested_amount,
            'payment_description': self.payment_description,
            'payment_type': 'debit',
            'state': 'pending',
        })
        seller_request_for_payment = settings.get('seller_request_for_payment')
        if seller_request_for_payment:
            template = request.env.ref('wbl_odoo_marketplace.mail_template_request_for_payment_admin')
            template.send_mail(seller_payment.id, force_send=True)

        return {
            'name': _('Seller Payment'),
            'view_mode': 'form',
            'view_id': self.env.ref('wbl_odoo_marketplace.view_seller_payment_form').id,
            'res_model': 'marketplace.seller.payment',
            'type': 'ir.actions.act_window',
            'res_id': seller_payment.id,  # Use the ID from the created record
        }
