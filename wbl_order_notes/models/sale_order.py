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

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order'

    order_message_field = fields.Text(string='Order Message Field')
    desire_date_field = fields.Date(string='Desirable Date Field')

    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        for order in self:
            for picking in order.picking_ids:
                picking.write({
                    'order_message_field': order.order_message_field,
                    'desire_date_field': order.desire_date_field,
                })
        return result
