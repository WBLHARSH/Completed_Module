import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class BraintreeController(http.Controller):
    _return_url = '/payment/braintree/return'

    @http.route(
        _return_url, type='http', auth='public', methods=['GET', 'POST'], csrf=False,
        save_session=False
    )
    def braintree_return_from_checkout(self, **data):
        _logger.info("Handling braintree processing with data:\n%s" % data)
        request.env['payment.transaction'].sudo()._handle_notification_data('braintree', data)
        return request.redirect('/payment/status')
