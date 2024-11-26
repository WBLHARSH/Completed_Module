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
        selection_add=[('thawani', "Thawani Payment Gateway")], ondelete={'thawani': 'set default'})
    thawani_secret_key = fields.Char(string="Thawani Secret Key", required_if_provider='thawani')
    thawani_publishable_key = fields.Char(string="Thawani Publishable Key", required_if_provider='thawani')

    def _thawani_get_api_url(self):

        self.ensure_one()

        if self.state == 'enabled':
            return 'https://checkout.thawani.om/'
        else:
            return 'https://uatcheckout.thawani.om/'