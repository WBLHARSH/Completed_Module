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
        selection_add=[('payTabs', "PayTabs Payment Gateway")], ondelete={'payTabs': 'set default'})
    payTabs_profile_id = fields.Char(string="PayTabs Profile Id", required_if_provider='payTabs')
    payTabs_secret_key = fields.Char(string="PayTabs Secret Key", required_if_provider='payTabs')


