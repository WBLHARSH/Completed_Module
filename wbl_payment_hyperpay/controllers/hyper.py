from odoo import http
from odoo.http import request
import requests
import json


class MyHyperController(http.Controller):
    @http.route('/HyperPay/checkout', type='json', auth='public', website=True)
    def hyperpay_checkout(self, is_valid=None):
        provider = request.env['payment.provider'].search([('code', '=', 'hyperPay')], limit=1)
        order = request.website.sale_get_order()
        partner = request.env.user.partner_id
        partner_name = partner.name.split(" ", 1)

        # Format the amount to 2 decimal places
        formatted_amount = f"{order.amount_total:.2f}"
        url = "https://eu-test.oppwa.com/v1/checkouts"
        data = {
            'entityId': provider.hyperpay_entity_id,
            'amount': formatted_amount,
            'currency': order.currency_id.name,
            'paymentType': 'DB',
            'customer.givenName': partner_name[0],
            'customer.surname': partner_name[1] if len(partner_name) > 1 else "",
            'customer.mobile': partner.phone,
            'customer.email': partner.email,
        }
        headers = {
            'Authorization': f'Bearer {provider.authorization_bearer}'
        }
        try:
            response = requests.post(url, data=data, headers=headers)
            response_json = response.json()
            check_id = response_json.get('id')
            return check_id
            # return response.json()  # Return the response as JSON
        except requests.HTTPError as e:
            return json.dumps({'error': str(e)})
        except requests.RequestException as e:
            return json.dumps({'error': str(e)})
