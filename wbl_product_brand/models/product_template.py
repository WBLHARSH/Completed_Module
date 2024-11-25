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

from odoo import models, fields, api


class ProductTemplate(models.Model):
    """
    This class extends the 'product.template' model to associate products with
    brands.
    """
    _inherit = 'product.template'

    brand_id = fields.Many2one('product.brand', string='Brand',
                               help="Name of the brand which the product"
                                    " belongs to")



    @api.onchange('brand_id')
    def _onchange_brand_id(self):
        pass


