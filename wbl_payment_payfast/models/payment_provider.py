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

from odoo import fields, models


class Paymentprovider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('payfast', "Payfast Payment Gateway")], ondelete={'payfast': 'set default'}
    )

    payfast_merchant_id = fields.Char(
        string="Payfast Merchant Id",
        required_if_provider='payfast')

    payfast_merchant_key = fields.Char(
        string="Payfast Merchant Key",
        required_if_provider='payfast')

    payfast_passphrase = fields.Char(
        string="Payfast Passphrase",
        required_if_provider='payfast')


    def _payfast_get_api_url(self):
        self.ensure_one()
        if self.state == 'enabled':
            return 'https://www.payfast.co.za/eng/process'
        else:
            return 'https://sandbox.payfast.co.za/eng/process'
