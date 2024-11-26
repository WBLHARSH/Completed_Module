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


class payfastController(http.Controller):
    _redirect_url = "/payment/payfast/redirect"
    _notify_url = "/payment/payfast/notify"
    cancel_url = "/payment/payfast/cancel"

    @http.route(
        [_redirect_url, cancel_url],
        type="http",
        auth="public",
    )
    def payfast_return_from_checkout(self, **data):
        """Handles the return from payfast and processes the notification."""

        tx_sudo = (
            request.env["payment.transaction"]
            .sudo()
            ._get_tx_from_notification_data("payfast", data)
        )
        tx_sudo._handle_notification_data("payfast", data)

        return request.redirect("/payment/status")

    @http.route(
        [_notify_url],
        type="http",
        auth="public",
    )
    def payfast_return_from_checkout_notify(self, **data):
        """Handles the return from payfast and processes the notification."""

        tx_sudo = (
            request.env["payment.transaction"]
            .sudo()
            ._get_tx_from_notification_data("payfast", data)
        )
        tx_sudo._handle_notification_data("payfast", data)

        return request.redirect("/payment/status")
