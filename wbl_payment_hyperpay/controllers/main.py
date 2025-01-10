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
import pprint

_logger = logging.getLogger(__name__)


class HyperpayController(http.Controller):
    """Handles responses from hyperpay"""

    _return_url = '/payment/hyperpay/return'
    _return_url_mada = '/payment/hyperpay/return_mada'

    @http.route(_return_url, type='http', auth='public', methods=['GET'], csrf=False, save_session=False)
    def hyperpay_return(self, **data):
        _logger.info("handling redirection from HyperPay with data:\n%s", pprint.pformat(data))
        request.env['payment.transaction'].sudo()._handle_notification_data('hyperpay', data)
        return request.redirect('/payment/status')

    @http.route(_return_url_mada, type='http', auth='public', methods=['GET'], csrf=False, save_session=False)
    def hyperpay_return_mada(self, **data):
        _logger.info("handling redirection from HyperPay with data:\n%s", pprint.pformat(data))
        request.env['payment.transaction'].sudo()._handle_notification_data('mada', data)
        return request.redirect('/payment/status')

    @http.route('/payment/hyperpay', website=True, type='http', auth='public', methods=['POST'], csrf=False,
                save_session=False)
    def hyperpay_payment_redirect(self, **post_data):
        provider = post_data.get('paymentMethodCode', 'hyperpay')
        form_values = {
            'payment_url': post_data.get('payment_url', False),
            'checkout_id': post_data.get('checkout_id', False),
            'amount': post_data.get('formatted_amount', False),
            'provider': provider,
        }
        if provider == 'mada':
            form_values.update({'return_url': self._return_url_mada, 'brands': 'MADA'})
        else:
            form_values.update({'return_url': self._return_url,
                                'brands': 'VISA MASTER AMEX ALIA ALIADEBIT APPLEPAY JCB MAESTRO DISCOVER MASTERDEBIT VISADEBIT CABAL BCMC'})
        return request.render('wbl_payment_hyperpay.wbl_hyperpay_payment_form', form_values)
