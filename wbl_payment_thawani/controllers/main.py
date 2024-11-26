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


import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ThawaniController(http.Controller):
    """Handles responses from thawani"""

    _redirect_url = "/payment/thawani/success"
    _cancel_url = "/payment/thawani/cancel"

    @http.route(
        [_redirect_url],
        type="http",
        auth="public",
    )
    def thawani_return_from_checkout(self, **data):
        """Handles the return from thawani and processes the notification."""
        _logger.info(f"Handling redirection from thawani with data\n{data}")

        tx_sudo = (
            request.env["payment.transaction"]
            .sudo()
            ._get_tx_from_notification_data("thawani", data)
        )
        tx_sudo._handle_notification_data("thawani", data)

        return request.redirect("/payment/status")


