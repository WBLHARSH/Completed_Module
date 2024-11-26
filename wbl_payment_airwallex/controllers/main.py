from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class WebsiteSaleInherit(WebsiteSale):
    @http.route('/shop/payment', type='http', auth='public', website=True, sitemap=False)
    def shop_payment(self, **post):
        response = super(WebsiteSaleInherit, self).shop_payment(**post)

        try:
            provider = request.env['payment.provider'].search([('code', '=', 'airwallex')], limit=1)
            base_url = provider.get_base_url()
            success_url = "payment/airwallex/return"
            cancel_url = "payment/airwallex/cancel"
            response.qcontext.update({
                'success_url': f"{base_url}{success_url}",
                'fail_url': f"{base_url}{cancel_url}",
            })
            return response

        except Exception as e:
            return response
