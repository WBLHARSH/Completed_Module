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

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductBrandProduct(models.Model):
    _name = 'brand.product.product'
    _description = 'Brand Product'

    product_brand_id = fields.Many2one('product.brand', string='Brand', ondelete='cascade', index=True)
    product_id = fields.Many2one('product.product', string='Product')
    image_128 = fields.Binary(string='Image 128', related='product_id.product_tmpl_id.image_128', store=True)
    product_reference = fields.Char(string='Reference', related='product_id.default_code')
    product_type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable Product'),
    ], string='Product Type', related='product_id.type')

    _sql_constraints = [
        ('unique_product_brand_product', 'unique(product_brand_id, product_id)',
         'A product can only be assigned to a brand once.')
    ]

    @api.constrains('product_brand_id', 'product_id')
    def _check_unique_product_for_brand(self):
        for record in self:
            existing_record = self.search([
                ('product_brand_id', '=', record.product_brand_id.id),
                ('product_id', '=', record.product_id.id),
                ('id', '!=', record.id)
            ])
            if existing_record:
                raise ValidationError('This product is already assigned to this brand.')

    @api.onchange('product_id')
    def _check_unique_products(self):
        for record in self:
            product = record.product_id.id
            brand_product_product = self.env['brand.product.product'].search([])
            for rec in brand_product_product:
                if product and rec.product_id.id == product:
                    raise ValidationError(
                        _('You cannot add this product as this product is already assigned to others'))
