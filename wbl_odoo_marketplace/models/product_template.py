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


class ProductTemplate(models.Model):
    _inherit = "product.template"

    seller_id = fields.Many2one(
        comodel_name='marketplace.seller',
        string='Seller',
        readonly=True,  # Making it optional initially
        ondelete='restrict',
    )

