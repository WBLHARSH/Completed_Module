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
from odoo.http import request
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_fee = fields.Char(string="Payment Fee")

    def _remove_payment_fee_line(self):
        """Remove delivery products from the sales orders"""
        payment_fee_lines = self.order_line.filtered("is_payment_fee")
        if not payment_fee_lines:
            return
        to_delete = payment_fee_lines.filtered(lambda x: x.qty_invoiced == 0)
        if not to_delete:
            raise UserError(
                _('You can not update the cod fee costs on an order where it was already invoiced!\n\nThe following delivery lines (product, invoiced quantity and price) have already been processed:\n\n')
                + '\n'.join(['- %s: %s x %s' % (
                    line.product_id.with_context(display_default_code=False).display_name, line.qty_invoiced,
                    line.price_unit) for line in payment_fee_lines])
            )
        to_delete.unlink()

    def _prepare_payment_fee_line_vals(self, payment_provider, price_unit):
        context = {}
        if self.partner_id:
            # set delivery detail in the customer language
            context['lang'] = self.partner_id.lang
            carrier = payment_provider.with_context(lang=self.partner_id.lang)
        product_id = request.env['product.product'].sudo().search([('default_code', '=', 'PAYMENT_FEE')], limit=1)
        # Apply fiscal position
        taxes = product_id.taxes_id.filtered(lambda t: t.company_id.id == self.company_id.id)
        taxes_ids = taxes.ids
        if self.partner_id and self.fiscal_position_id:
            taxes_ids = self.fiscal_position_id.map_tax(taxes).ids

        # Create the sales order line

        if product_id.description_sale:
            so_description = '%s: %s' % (payment_provider.name, product_id.description_sale)
        else:
            so_description = payment_provider.name
        values = {
            'order_id': self.id,
            'name': so_description,
            'price_unit': price_unit,
            'product_uom_qty': 1,
            'product_uom': product_id.uom_id.id,
            'product_id': product_id.id,
            'tax_id': [(6, 0, taxes_ids)],
            'is_payment_fee': True,
        }
        return values

    def _create_payment_fee_line(self, payment_provider, price_unit):
        values = self._prepare_payment_fee_line_vals(payment_provider, price_unit)
        return self.env['sale.order.line'].sudo().create(values)
