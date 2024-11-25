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


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_brand_name_on_product_page = fields.Boolean(string='show brand name on product page')
    show_brand_name_on_shop_page = fields.Boolean(string='show brand name on shop page')
    show_brand_name_on_website_menu = fields.Boolean(string='show brand name on website menu')
    show_brand_name_on_category_page = fields.Boolean(string='show brand name on category page')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrConfigParam = self.env['ir.config_parameter'].sudo()

        res.update(
            show_brand_name_on_product_page=IrConfigParam.get_param(
                'res.config.settings.show_brand_name_on_product_page', default=''),
            show_brand_name_on_shop_page=IrConfigParam.get_param('res.config.settings.show_brand_name_on_shop_page',
                                                                 default=''),
            show_brand_name_on_website_menu=IrConfigParam.get_param(
                'res.config.settings.show_brand_name_on_website_menu',
                default=''),
            show_brand_name_on_category_page=IrConfigParam.get_param(
                'res.config.settings.show_brand_name_on_category_page', default=False),

        )

        return res

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrConfigParam = self.env['ir.config_parameter'].sudo()

        IrConfigParam.set_param('res.config.settings.show_brand_name_on_product_page',
                                self.show_brand_name_on_product_page)
        IrConfigParam.set_param('res.config.settings.show_brand_name_on_shop_page', self.show_brand_name_on_shop_page)
        IrConfigParam.set_param('res.config.settings.show_brand_name_on_website_menu',
                                self.show_brand_name_on_website_menu)
        IrConfigParam.set_param('res.config.settings.show_brand_name_on_category_page',
                                self.show_brand_name_on_category_page)


class WebsiteMenu(models.Model):
    _inherit = 'website.menu'

    @api.model
    def get_menu_items(self):
        menu_items = super(WebsiteMenu, self).get_menu_items()
        config_settings = self.env['res.config.settings'].sudo().get_values()
        show_menu = config_settings.get('show_brand_name_on_website_menu', False)

        if not show_menu:
            menu_items = [item for item in menu_items if
                          item.id != self.env.ref('wbl_product_brand.wbl_buy_again_menu').id]

        return menu_items
