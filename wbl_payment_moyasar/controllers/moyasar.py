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

from odoo import http
from odoo.http import request


class MoyasarController(http.Controller):
    _redirect_url = "/payment/moyasar/redirect"

    @http.route('/payment/moyasar/response', type='http', auth='public',
                website=True, csrf=False, save_session=False)
    def moyasar_payment_response(self, **data):

        return request.render(
            "wbl_payment_moyasar.moyasar_payment_gateway_form_render",
            {"publishable_api_key": data.get('publishable_api_key'),
             "currency": data.get('currency'),
             "amount": data.get('amount'),
             "description": data.get('description'),
             "callback_url": data.get('callback_url'),
             }
        )

    @http.route(
        [_redirect_url],
        type="http",
        auth="public",
    )
    def moyasar_return_from_checkout(self, **data):
        """Handles the return from moyasar and processes the notification."""

        tx_sudo = (
            request.env["payment.transaction"]
            .sudo()
            ._get_tx_from_notification_data("moyasar", data)
        )
        tx_sudo._handle_notification_data("moyasar", data)

        return request.redirect("/payment/status")
