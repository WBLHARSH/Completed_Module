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

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    abidjan = fields.Many2one("abidjan", string='Abidjan')
    ivory_coast = fields.Many2one("ivory.coast", string='Ivory Coast')
    country = fields.Many2one('country.details', string='Country')
    selected_option = fields.Char(string='Selected Option')
    address = fields.Text(string='Address')
