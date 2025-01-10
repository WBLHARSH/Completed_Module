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


import json
import logging

from odoo import api, fields, models, _

from urllib.parse import urlencode
from urllib.request import build_opener, Request, HTTPHandler
from urllib.error import HTTPError, URLError

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('hyperpay', "HyperPay")], ondelete={'hyperpay': 'set default'})
    hyperpay_merchant_id = fields.Char(string='Entity ID')
    hyperpay_merchant_id_mada = fields.Char(string='Entity ID (MADA)')
    hyperpay_authorization_bearer = fields.Char(string="Authorization Bearer", required_if_provider='hyperpay')

    def _hyperpay_get_api_url(self):
        self.ensure_one()
        if self.state == 'enabled':
            return 'https://eu-prod.oppwa.com/'
        else:
            return 'https://eu-test.oppwa.com/'

    def _hyperpay_make_checkout_request(self, data):
        self.ensure_one()
        try:
            hyper_url = self._hyperpay_get_api_url()
            url = f"{hyper_url}v1/checkouts"
            opener = build_opener(HTTPHandler)
            request = Request(url, data=urlencode(data).encode('utf-8'))
            request.add_header('Authorization', 'Bearer %s' % self.hyperpay_authorization_bearer)
            request.get_method = lambda: 'POST'
            response = opener.open(request)
            return json.loads(response.read())
        except HTTPError as e:
            return json.loads(e.read())
        except URLError as e:
            return e.reason

    def _hyperpay_get_payment_checkout_status(self, url, provider_code):
        merchant_id = self.hyperpay_merchant_id_mada if provider_code == 'mada' else self.hyperpay_merchant_id
        url += '?entityId=%s' % merchant_id
        try:
            opener = build_opener(HTTPHandler)
            request = Request(url, data=b'')
            request.add_header('Authorization', 'Bearer %s' % self.hyperpay_authorization_bearer)
            request.get_method = lambda: 'GET'
            response = opener.open(request)
            return json.loads(response.read())
        except HTTPError as e:
            return json.loads(e.read())
        except URLError as e:
            return e.reason