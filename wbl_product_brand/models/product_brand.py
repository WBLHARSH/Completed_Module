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


class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = 'Product Brand'

    name = fields.Char(string='Brand Name', required=True)
    banner_image = fields.Binary(string='Banner Image')
    brand_logo = fields.Image()
    is_published = fields.Boolean(string='Is Published', default=True)
    products = fields.One2many('brand.product.product', inverse_name='product_brand_id', string='Products')
    pro_item_count = fields.Integer(string="Number Of Count", compute="_compute_item_count", store=True)
    description = fields.Html(string='Description')
    description_truncated = fields.Char(compute='_compute_description_truncated', string='Truncated Description',
                                        store=False)

    @api.constrains('products')
    def _onchange_products(self):
        product_templates = self.products.mapped('product_id.product_tmpl_id')
        products = self.env['product.template'].browse(product_templates.ids)
        for product in products:
            product.write({'brand_id': self.id})

    @api.depends('products')
    def _compute_item_count(self):
        for record in self:
            record.pro_item_count = len(record.products)

    @api.depends('description')
    def _compute_description_truncated(self):
        for record in self:
            if record.description:
                # Strip HTML tags and split by words
                import re
                text = re.sub(r'<[^>]+>', '', record.description)  # Remove HTML tags
                words = text.split()
                if len(words) > 3:
                    record.description_truncated = ' '.join(words[:3]) + '...'
                else:
                    record.description_truncated = text
            else:
                record.description_truncated = ''

    def toggle_published(self):
        for record in self:
            record.is_published = not record.is_published

    def action_open_products(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Products',
            'res_model': 'brand.product.product',
            'view_mode': 'kanban',
            'view_id': self.env.ref('wbl_product_brand.view_product_kanban').id,
            'target': 'current',
            'domain': [('product_brand_id', '=', self.id)],
        }
