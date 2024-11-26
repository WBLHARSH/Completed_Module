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


from odoo import fields, models, api


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    enable_payment_fee = fields.Boolean(string="Enable Payment Fee", default=False, help='Enable Payment Fee Tab')
    # Fee By Customer
    partner_ids = fields.Many2many('res.partner', string="Customers",
                                   help='Payment Fee will be added for selected Customers only.')
    # Fee By Product
    products_ids = fields.Many2many('product.product', string="Products",
                                    help='Payment Fee will be added for selected Product only.')
    # Fee By Website
    website_ids = fields.Many2many('website', string="Websites",
                                   help='Payment Fee will be added for selected Website only.')
    # Fee By Country
    country_ids = fields.Many2many('res.country', string="Countries",
                                   help='Payment Fee will be added for selected Country only.')
    # General Group
    fee = fields.Selection(selection=[('fixed_amount', 'Fixed Amount'), ('order_percentage', 'Order Percentage')],
                           string="Fee Type")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)
    fee_amount = fields.Monetary(string='Fees Amount', currency_field='currency_id',
                                 help='Payment Fee will be added for selected Fee Amount.')
    fee_percentage = fields.Float(string='Fees Percentage',
                                  help='Payment Fee will be added for selected Fee Percentage.')
    payment_fee_product = fields.Many2one('product.product', string='Payment Fee Product',
                                          help='The product used to add payment fee.')
    # Fee By Order Amount
    minimum_order_amount = fields.Monetary(string='Minimum Order Amount', currency_field='currency_id',
                                           help='Payment Fee will be added for selected Minimum Order Amount.')
    tax_excluded = fields.Boolean(string="Tax Excluded", default=False)
    # Fee By Calender
    from_date = fields.Date(string="From", help='Payment Fee will be added for From Date.')
    to_date = fields.Date(string="To", help='Payment Fee will be added for To Date.')

    @api.model
    def create(self, vals):
        if not vals.get('payment_fee_product'):
            payment_fee_product = self.env.ref('wbl_payment_fee.payment_fee_product',
                                               raise_if_not_found=False)
            if payment_fee_product:
                vals['payment_fee_product'] = payment_fee_product.id
        return super(PaymentProvider, self).create(vals)

    def write(self, vals):
        if not self.payment_fee_product:
            payment_fee_product = self.env.ref('wbl_payment_fee.payment_fee_product',
                                               raise_if_not_found=False)
            if payment_fee_product:
                vals['payment_fee_product'] = payment_fee_product.id
        return super(PaymentProvider, self).write(vals)

    # @api.onchange('fee_amount')
    # def _onchange_fee_amount(self):
    #     """Update the fee_amount in payment.method when changed in payment.provider."""
    #     for provider in self:
    #         payment_methods = self.env['payment.method'].search([
    #             ('payment_provider_id', '=', provider.id)  # Ensure this relation exists
    #         ])
    #         for method in payment_methods:
    #             method.fee_amount = provider.fee_amount
    #
    # @api.model
    # def create(self, vals):
    #     """Override create to set fee_amount in payment.method."""
    #     record = super(PaymentProvider, self).create(vals)
    #     self._update_payment_method_fee(record)
    #     return record
    #
    # def write(self, vals):
    #     """Override write to set fee_amount in payment.method."""
    #     res = super(PaymentProvider, self).write(vals)
    #     if 'fee_amount' in vals:
    #         for provider in self:
    #             self._update_payment_method_fee(provider)
    #     return res
    #
    # def _update_payment_method_fee(self, provider):
    #     """Update fee_amount in payment.method."""
    #     payment_methods = self.env['payment.method'].search([
    #         ('payment_provider_id', '=', provider.id)
    #     ])
    #     for method in payment_methods:
    #         method.fee_amount = provider.fee_amount
