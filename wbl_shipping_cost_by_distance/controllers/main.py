from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http, _
from odoo.http import request
import random


class WebsiteSaleInherit(WebsiteSale):

    # ===================== Save Hard Code Data In Address Form =========================
    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True,
                sitemap=False)
    def address(self, **kw):
        response = super(WebsiteSaleInherit, self).address(**kw)
        order = request.website.sale_get_order()
        if order:
            order.distance_amount = ''
        return response
