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
        selection_add=[('moyasar', "Moyasar Payment Gateway")], ondelete={'moyasar': 'set default'}
    )

    moyasar_public_key = fields.Char(
        string="Moyasar Public Key",
        required_if_provider='moyasar')

    moyasar_secret_key = fields.Char(
        string="Moyasar Secret Key",
        required_if_provider='moyasar')
