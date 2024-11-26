from odoo import http
from odoo.http import request
import uuid, requests


class KlarnaController(http.Controller):
    _redirect_url = "/payment/klarna/redirect"

    @http.route('/payment/klarna/response', type='http', auth='public',
                website=True, csrf=False, save_session=False)
    def klarna_payment_response(self, **data):
        html = {
            'data': data.get('data')
        }
        return request.render(
            "wbl_payment_klarna.klarna_payment_gateway_form_render", html)

    @http.route(
        [_redirect_url],
        type="http",
        auth="public",
    )
    def klarna_return_from_checkout(self, **data):
        """Handles the return from klarna and processes the notification."""

        tx_sudo = (
            request.env["payment.transaction"]
            .sudo()
            ._get_tx_from_notification_data("klarna", data)
        )
        tx_sudo._handle_notification_data("klarna", data)

        return request.redirect("/payment/status")
