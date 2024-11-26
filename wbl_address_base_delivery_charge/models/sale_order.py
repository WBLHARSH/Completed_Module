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


from odoo import models, fields, _, api
from odoo.exceptions import UserError
from odoo.http import request


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_address = fields.Text(related='partner_id.address', string='Partner Address')
    partner_selected_option = fields.Char(related='partner_id.selected_option', string='Partner Option')
    partner_abidjan = fields.Many2one(related='partner_id.abidjan', string='Partner Abidjan')
    partner_ivory_coast = fields.Many2one(related='partner_id.ivory_coast', string='Partner Ivory Coast')
    partner_country = fields.Many2one(related='partner_id.country', string='Partner Country')
    additional_price = fields.Float(string='Additional Price', default=0.0)
