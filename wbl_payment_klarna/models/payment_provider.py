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
        selection_add=[('klarna', "Klarna Payment Gateway")], ondelete={'klarna': 'set default'}
    )

    klarna_username = fields.Char(
        string="Klarna Username",
        required_if_provider='klarna')

    klarna_password = fields.Char(
        string="Klarna Password",
        required_if_provider='klarna')

    def _klarna_get_api_url(self):

        self.ensure_one()

        if self.state == 'enabled':
            return 'https://api.klarna.com/'
        else:
            return 'https://api.playground.klarna.com/'