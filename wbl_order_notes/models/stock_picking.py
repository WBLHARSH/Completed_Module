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

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = 'Sale Order'

    order_message_field = fields.Text(string='Order Message Field')
    desire_date_field = fields.Date(string='Desirable Date Field')
