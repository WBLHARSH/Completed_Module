from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class WebsiteSaleInherit(WebsiteSale):
    @http.route('/shop/payment', type='http', auth='public', website=True, sitemap=False)
    def shop_payment(self, **post):
        response = super(WebsiteSaleInherit, self).shop_payment(**post)
        try:

            gateway = self._get_braintree_gateway()
            client_token = gateway.client_token.generate()
            response.qcontext.update({
                'client_token': str(client_token),
            })
            return response

        except Exception as e:
            return response

    def _get_braintree_gateway(self):
        try:
            provider = request.env['payment.provider'].search([('code', '=', 'braintree')], limit=1)
            if not provider:
                raise ValueError("Braintree payment provider not configured.")

            from braintree import BraintreeGateway, Configuration
            return BraintreeGateway(Configuration(
                environment="sandbox",
                merchant_id=provider.braintree_merchant_id,
                public_key=provider.braintree_public_key,
                private_key=provider.braintree_private_key
            ))

        except Exception as e:
            raise


class MyBraintreeController(http.Controller):
    @http.route('/braintree/payment/process', type='json', auth='public', website=True)
    def braintree(self, paymentMethodNonce):
        order = request.website.sale_get_order()
        provider = request.env['payment.provider'].search([('code', '=', 'braintree')], limit=1)
        import braintree
        simulated_nonce = paymentMethodNonce
        amount = str(order.amount_total)
        braintree.Configuration.configure(
            environment=braintree.Environment.Sandbox,
            merchant_id=provider.braintree_merchant_id,
            public_key=provider.braintree_public_key,
            private_key=provider.braintree_private_key
        )
        transaction_request = {
            'amount': amount,
            'payment_method_nonce': simulated_nonce,
            'options': {
                'submit_for_settlement': True
            }
        }
        result = braintree.Transaction.sale(transaction_request)
        if result.is_success:
            order = request.website.sale_get_order()
            order.write(
                {'braintree_txn_id': result.transaction.id, 'braintree_txn_status': result.transaction.status})
            return {
                'result': 'success',
            }
        return {
            'result': 'fail',
        }
