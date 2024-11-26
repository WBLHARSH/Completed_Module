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


class PayfastCommon(PaymentCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.payfast = cls._prepare_provider('payfast', update_values={
            'payfast_merchant_id': 'dummy',
            'payfast_merchant_key': 'dummy',
        })
        cls.provider = cls.payfast
        cls.currency = cls.currency_euro
        cls.notification_data = {
            'ref': cls.reference,
            'id': 'fdff13af-fa07-486d-98ea-76ffdf8d7673',
        }
