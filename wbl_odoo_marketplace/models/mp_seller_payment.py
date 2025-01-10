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

from odoo import fields, models, api, _
from odoo.http import request
from odoo.exceptions import UserError


class MarketplaceSellerPayment(models.Model):
    _name = 'marketplace.seller.payment'
    _description = "Marketplace Seller Payment"
    _rec_name = 'seller_payment_reference'
    _order = 'create_date desc'

    seller_payment_reference = fields.Char(string='Payment reference')
    user_id = fields.Many2one(comodel_name='res.users')
    seller_id = fields.Many2one(comodel_name='marketplace.seller', string='Seller')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)
    invoice_id = fields.Many2one(comodel_name='account.move', string='invoice')

    payment_amount = fields.Monetary(string="Payment Amount", currency_field='currency_id')
    payment_description = fields.Text(string="Payment Description")
    invoice_count = fields.Integer(string='Invoice Count',
                                   compute='_compute_invoice_count')

    payment_type = fields.Selection(
        selection=[
            ('credit', 'Credit'),
            ('debit', 'Debit')],
        string="Payment Type")

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('denied', 'Denied'),
        ],
        string='Status',
        required=True,
        readonly=True,
        group_expand='_expand_states',
        copy=False,
        default='draft',
    )

    display_amount = fields.Char(string="Payable Amount", compute="_compute_display_amount", store=True)

    @api.depends('invoice_id')
    def _compute_invoice_count(self):
        pickings = self.env['account.move'].sudo().search([
            ('id', '=', self.invoice_id.id),
            ('seller_id', '=', self.seller_id.id)
        ])

        for line in self:
            line.invoice_count = len(pickings)

    @api.depends('payment_type', 'payment_amount')
    def _compute_display_amount(self):
        for record in self:
            if record.payment_type == 'debit':
                record.display_amount = f"{record.currency_id.symbol} -{record.payment_amount:,.2f}"
            else:
                record.display_amount = f"{record.currency_id.symbol} {record.payment_amount:,.2f}"

    def _expand_states(self, states, domain, order):
        return [key for key, val in self._fields['state'].selection]

    def action_payment_request_approved(self):
        for rec in self:
            if rec.payment_type == 'debit':

                cashable_amount = self._compute_final_amount()
                if rec.payment_amount > cashable_amount:
                    raise UserError(_("Seller have not enough amount."))
                invoice_id = self.create_seller_payment_invoice(rec)
                rec.invoice_id = invoice_id.id
                rec.state = 'approved'
                self._send_seller_payment_state_notification(rec.id, "Approved")
                return {
                    'name': _('Customer Invoice'),
                    'view_mode': 'form',
                    'view_id': self.env.ref('account.view_move_form').id,
                    'res_model': 'account.move',
                    'context': "{'move_type':'out_invoice'}",
                    'type': 'ir.actions.act_window',
                    'res_id': rec.invoice_id.id,
                }

            if rec.payment_type == 'credit':
                rec.state = 'approved'

    def action_payment_request_denied(self):
        for rec in self:
            rec.state = 'denied'
            self._send_seller_payment_state_notification(rec.id, "Denied")

    def create_seller_payment_invoice(self, rec):
        product_id = request.env['product.product'].sudo().search([('default_code', '=', 'SellerPayment_012')], limit=1)
        delivey_invoice = self.env['account.move'].create([
            {
                'move_type': 'out_invoice',
                'invoice_date': fields.Date.context_today(self),
                'partner_id': self.seller_id.partner_id.id,
                'currency_id': self.currency_id.id,
                'amount_total': self.payment_amount,
                'seller_id': self.seller_id.id,
                'invoice_user_id': self.seller_id.user_id.id,
                'invoice_line_ids': [
                    (0, None, {
                        'product_id': product_id.id,
                        'name': 'Marketplace Seller Payment',
                        'quantity': 1,
                        'price_unit': self.payment_amount,
                        'price_subtotal': self.payment_amount,
                    }),
                ],
            },
        ])
        return delivey_invoice

    def action_view_seller_invoice(self):
        return {
            'name': _('Customer Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': "{'move_type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'res_id': self.invoice_id.id,
        }

    def _compute_final_amount(self):
        if self.seller_id:
            total_credit = sum(self.env['marketplace.seller.payment'].search([
                ('seller_id', '=', self.seller_id.id),
                ('payment_type', '=', 'credit'),
                ('state', '=', 'approved'),
            ]).mapped('payment_amount'))

            total_debit = sum(self.env['marketplace.seller.payment'].search([
                ('seller_id', '=', self.seller_id.id),
                ('payment_type', '=', 'debit'),
                ('state', '=', 'approved'),
            ]).mapped('payment_amount'))

            return total_credit - total_debit
        else:
            return 0

    def _send_seller_payment_state_notification(self, payment_id, state):
        # Settings
        settings = request.env['res.config.settings'].sudo().get_values()
        notify_seller_payment_approved = settings.get(
            'seller_payment_request_approved_notify_to_seller')
        # Mail An Notification
        notify_admin_payment_denied = settings.get(
            'seller_payment_request_denied_notify_to_seller')
        if state == "Approved" and notify_seller_payment_approved:
            template = request.env.ref('wbl_odoo_marketplace.mail_template_seller_payment_request_approved')
            template.send_mail(payment_id, force_send=True)
        elif state == "Denied" and notify_admin_payment_denied:
            template = request.env.ref('wbl_odoo_marketplace.mail_template_seller_payment_request_denied')
            template.send_mail(payment_id, force_send=True)
