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


from odoo import fields, models, api, _
import requests
import json
import hmac
import hashlib
import requests
import uuid
import logging

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    code = fields.Selection(
        selection_add=[('saferPay', "SaferPay Payment Gateway")], ondelete={'saferPay': 'set default'})
    saferPay_username = fields.Char(string="Username", required_if_provider='saferPay')
    saferPay_password = fields.Char(string="Password", required_if_provider='saferPay')
    saferPay_customer_id = fields.Char(string="Customer ID", required_if_provider='saferPay')
    saferPay_terminal_id = fields.Char(string="Terminal ID", required_if_provider='saferPay')

    def _saferpay_get_api_url(self):
        self.ensure_one()
        if self.state == 'enabled':
            return 'https://saferpay.com/api/'
        else:
            return 'https://test.saferpay.com/api/'
