from odoo import models, api, tools


class Menu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
    def _visible_menu_ids(self, debug=False):
        menus = super(Menu, self)._visible_menu_ids(debug)
        pending_seller_group = self.env.user.has_group('wbl_odoo_marketplace.group_marketplace_pending_seller')
        user_group = self.env.user.has_group('wbl_odoo_marketplace.group_marketplace_user')
        if user_group:
            for menu in menus:
                menu_obj = self.env['ir.ui.menu'].browse(menu)
                if menu_obj.name == 'Request For Payment':
                    menus.remove(menu_obj.id)
                    break
        # Exclude 'My Shop Profile' menu for user groups
        if user_group:
            for menu in menus:
                menu_obj = self.env['ir.ui.menu'].browse(menu)
                if menu_obj.name == 'My Shop Profile':
                    menus.remove(menu_obj.id)
                    break

        elif pending_seller_group:
            seller_menus = [
                'Marketplace',
                'Dashboard',
                'Sellers',
                'My Shop Profile',
                'Customer Queries',
                'Catalog',
                'Products',
                'Sales',
                'Orders',
                'Request For Payment',
                'Seller Payments',
                'Invoicing',
                'Invoices',
                'Inventory',
                'Delivery Orders',
                'Website',
                'Site',
                'Homepage'
            ]
            seller_allow_menus = set()
            for menu in menus:
                menu_obj = self.env['ir.ui.menu'].browse(menu)
                if menu_obj.name in seller_menus:
                    seller_allow_menus.add(menu)
            return seller_allow_menus
        return menus
