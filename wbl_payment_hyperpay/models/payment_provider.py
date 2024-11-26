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
        selection_add=[('hyperPay', "HyperPay Payment Gateway")], ondelete={'hyperPay': 'set default'})
    hyperpay_entity_id = fields.Char(string="HyperPay Entity ID", required_if_provider='hyperPay')
    authorization_bearer = fields.Char(string="Authorization Bearer", required_if_provider='hyperPay')

    def _hyperpay_get_api_url(self):

        self.ensure_one()

        if self.state == 'enabled':
            return 'https://eu-prod.oppwa.com/'
        else:
            return 'https://eu-test.oppwa.com/'
