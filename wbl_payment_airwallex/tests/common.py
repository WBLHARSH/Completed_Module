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


from odoo.addons.payment.tests.common import PaymentCommon


class AirwallexCommon(PaymentCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.airwallex = cls._prepare_provider('airwallex', update_values={
            'airwallex_client_id': 'dummy',
            'airwallex_api_key': 'dummy',
        })
        cls.provider = cls.airwallex
        cls.currency = cls.currency_euro

        cls.notification_data = {
            'ref': cls.reference,
            'id': 'tr_ABCxyz0123',
        }
