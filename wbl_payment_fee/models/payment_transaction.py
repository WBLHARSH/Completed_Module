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


from odoo import models, fields


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)
    payment_fee = fields.Monetary(string="Payment Fee", currency_field='currency_id')

    def _create_payment(self):
        res = super(PaymentTransaction, self)._create_payment()
        provider = self.provider_id
        if provider.enable_payment_fee:
            sale_order = self.env['sale.order'].search([('name', '=', self.reference)])
            if sale_order.payment_fee:
                self.payment_fee = round(float(sale_order.payment_fee), 2)
        return res
