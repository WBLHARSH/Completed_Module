
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class HyperPayController(http.Controller):
    """Handles responses from payTabs"""

    _redirect_url = "/payment/hyperPay/redirect"

    @http.route(
        [_redirect_url],
        type="http",
        auth="public",
    )
    def hyperPay_return_from_checkout(self, **data):
        """Handles the return from payTabs and processes the notification."""
        _logger.info(f"Handling redirection from payTabs with data\n{data}")

        tx_sudo = (
            request.env["payment.transaction"]
            .sudo()
            ._get_tx_from_notification_data("hyperPay", data)
        )
        tx_sudo._handle_notification_data("hyperPay", data)

        return request.redirect("/payment/status")
