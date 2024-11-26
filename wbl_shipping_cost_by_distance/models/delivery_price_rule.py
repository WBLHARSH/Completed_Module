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

class PriceRule(models.Model):
    _inherit = "delivery.price.rule"

    # Extending the selection field to include 'distance'
    variable = fields.Selection(
        selection_add=[('distance', 'Distance')],
        ondelete={'distance': 'set default'}
    )
    variable_factor = fields.Selection(
        selection_add=[('distance', 'Distance')],
        ondelete={'distance': 'set default'}
    )
    distance_unit = fields.Selection(selection=[('km', 'KM'), ('miles', 'Miles')], default='km')

