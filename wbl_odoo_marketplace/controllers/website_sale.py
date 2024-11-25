from odoo.http import request
from odoo.addons.website_sale.controllers import main


class WebsiteSale(main.WebsiteSale):

    def _prepare_product_values(self, product, category, search, **kwargs):
        values = super()._prepare_product_values(product, category, search, **kwargs)
        product_product = request.env['product.product'].sudo().search([('product_tmpl_id', '=', product.id)], limit=1)
        mp_product = request.env['mp.seller.product'].sudo().search([('product_id', '=', product_product.id)], limit=1)
        if mp_product:
            values['seller'] = mp_product.seller_id
            values['seller_profile'] = '/seller/profile/' + mp_product.seller_id.shop_url
        return values
