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

from odoo import fields, models, tools, api
from odoo.tools.translate import html_translate


class MarketplaceSellerProduct(models.Model):
    _name = 'mp.seller.product'
    _description = "Marketplace Seller Product"

    user_id = fields.Many2one(comodel_name='res.users', string='User', required=True)
    seller_id = fields.Many2one(comodel_name='marketplace.seller', string='Seller', required=True)
    product_id = fields.Many2one(comodel_name='product.product', string='Product')
    name = fields.Char(string='Name')
    image_1920 = fields.Image('Image')
    detailed_type = fields.Selection([
        ('consu', 'Consumable'),
        ('product', 'Storable Product'),
        ('service', 'Service')], string='Product Type', default='consu', required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)
    list_price = fields.Float(
        'Sales Price', default=1.0,
        digits='Product Price',
        help="Price at which the product is sold to customers.",
    )

    default_code = fields.Char(string='Internal Reference')
    website_id = fields.Many2one(
        "website",
        string="Website",
        ondelete="restrict",
        help="Restrict publishing to this website.",
        index=True,
    )

    @tools.ormcache()
    def _get_default_category_id(self):
        # Deletion forbidden (at least through unlink)
        return self.env.ref('product.product_category_all')

    categ_id = fields.Many2one(
        'product.category', 'Product Category',
        change_default=True, default=_get_default_category_id,
        required=True)
    taxes_id = fields.Many2many('account.tax',
                                help="Default taxes used when selling the product.", string='Customer Taxes')
    description = fields.Html(string='Description', translate=True)
    attribute_line_ids = fields.One2many('product.template.attribute.line', 'product_tmpl_id', 'Product Attributes',
                                         copy=True)
    seller_product_image_ids = fields.One2many(
        string="Extra Product Media",
        comodel_name='seller.product.image',
        inverse_name='seller_product_id',
        copy=True,
    )
    allow_out_of_stock_order = fields.Boolean(string='Continue selling when out-of-stock', default=True)

    available_threshold = fields.Float(string='Show Threshold', default=5.0)
    show_availability = fields.Boolean(string='Show availability Qty', default=False)
    out_of_stock_message = fields.Html(string="Out-of-Stock Message", translate=html_translate)
    initial_stock = fields.Float(string='Initial Stock',
                                 digits='Product Unit of Measure', compute_sudo=False,
                                 help="Initial quantity of products.\n")
    qty_available = fields.Float(string='Quantity On Hand',
                                 digits='Product Unit of Measure', compute_sudo=False,
                                 help="Current quantity of products.\n"
                                      "In a context with a single Stock Location, this includes "
                                      "goods stored at this Location, or any of its children.\n"
                                      "In a context with a single Warehouse, this includes "
                                      "goods stored in the Stock Location of this Warehouse, or any "
                                      "of its children.\n"
                                      "stored in the Stock Location of the Warehouse of this Shop, "
                                      "or any of its children.\n"
                                      "Otherwise, this includes goods stored in any Stock Location "
                                      "with 'internal' type.")
    virtual_available = fields.Float(string='Forecasted Quantity',
                                     digits='Product Unit of Measure', compute_sudo=False,
                                     help="Forecast quantity (computed as Quantity On Hand "
                                          "- Outgoing + Incoming)\n"
                                          "In a context with a single Stock Location, this includes "
                                          "goods stored in this location, or any of its children.\n"
                                          "In a context with a single Warehouse, this includes "
                                          "goods stored in the Stock Location of this Warehouse, or any "
                                          "of its children.\n"
                                          "Otherwise, this includes goods stored in any Stock Location "
                                          "with 'internal' type.")

    description_pickingout = fields.Text('Description on Delivery Orders', translate=True)
    description_pickingin = fields.Text('Description on Receptions', translate=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('denied', 'Denied'),
        ],
        string='Status',
        required=True,
        readonly=True,
        group_expand='_expand_states',
        copy=False,
        default='draft',
    )

    def _expand_states(self, states, domain, order):
        return [key for key, val in self._fields['state'].selection]

    @api.model_create_multi
    def create(self, vals_list):
        # Retrieve the product auto-approval setting once
        auto_approval = self.env['ir.config_parameter'].sudo().get_param('wbl_odoo_marketplace.product_auto_approval',
                                                                         default='False') == 'True'
        user_id = self.env.user.id
        seller = self.env['marketplace.seller'].sudo().search([('user_id', '=', user_id)], limit=1) if user_id else None

        for vals in vals_list:
            vals.update({
                'user_id': user_id,
                'seller_id': seller.id if seller else False,
            })
            if auto_approval:
                vals['state'] = 'approved'

        products = super(MarketplaceSellerProduct, self).create(vals_list)
        if auto_approval:
            for product in products:
                odoo_product = self.sudo()._create_mp_product(product)
                product.write({'product_id': odoo_product.id})

        return products

    def action_product_approval_request(self):
        for rec in self:
            rec.state = 'pending'

    def action_product_approved(self):
        for rec in self:
            rec.state = 'approved'
            odoo_product = self._create_mp_product(rec)
            rec.write({'product_id': odoo_product.id})

    def action_product_denied(self):
        for rec in self:
            rec.state = 'denied'

    def _create_product_images(self, mp_product, product):
        """
        Creates product.image records based on the images in mp_product.seller_product_image_ids.
        """
        image_ids = []
        for seller_image in mp_product.seller_product_image_ids:
            new_image = self.env['product.image'].create({
                'name': seller_image.name,
                'image_1920': seller_image.image_1920,
                'sequence': seller_image.sequence,
                'video_url': seller_image.video_url,
                'embed_code': seller_image.embed_code,
                'can_image_1024_be_zoomed': seller_image.can_image_1024_be_zoomed,
                'product_tmpl_id': product.product_tmpl_id.id,  # Link to the newly created product template
            })
            image_ids.append(new_image.id)
        return image_ids

    def create_initial_stock(self, product, mp_product):
        """
                Creates stock.quant records based on the product type in mp_product.initial_stock.
        """
        warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.company.id)], limit=1
        )
        self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id': product.id,
            'location_id': warehouse.lot_stock_id.id,
            'inventory_quantity': mp_product.initial_stock,
        }).action_apply_inventory()
        return True

    def _create_mp_product(self, mp_product):
        product = self.env['product.product'].create({
            'name': mp_product.name,
            'list_price': mp_product.list_price,
            'website_published': True,
            'type': mp_product.detailed_type,
            'image_1920': mp_product.image_1920,
            'categ_id': mp_product.categ_id.id,
            'default_code': mp_product.default_code,
            'website_id': mp_product.website_id,
            'taxes_id': [(6, 0, mp_product.taxes_id.ids)],
            'description': mp_product.description,
            'description_pickingin': mp_product.description_pickingin,
            'description_pickingout': mp_product.description_pickingout,
            'show_availability': mp_product.show_availability,
            'out_of_stock_message': mp_product.out_of_stock_message,

        })
        image_ids = self._create_product_images(mp_product, product)
        product.product_template_image_ids = [(6, 0, image_ids)]

        # Here we store the on hand quantity of product
        if mp_product.detailed_type == "product":
            self.create_initial_stock(product, mp_product)

        return product
