from odoo import models, api, tools


class Website(models.Model):
    _inherit = 'website'

    @tools.ormcache('self.env.uid', 'self.id')
    def _get_menu_ids(self):
        menus = super(Website, self)._get_menu_ids()
        show_brand_name_on_website_menu = self.env['ir.config_parameter'].sudo().get_param(
            'res.config.settings.show_brand_name_on_website_menu',
            default='False'
        )
        filtered_menus = []

        for menu in menus:
            web_menu = self.env['website.menu'].browse(menu)
            if web_menu.name == 'Brands':
                if show_brand_name_on_website_menu == "True":
                    filtered_menus.append(menu)
            else:
                filtered_menus.append(menu)

        return filtered_menus
