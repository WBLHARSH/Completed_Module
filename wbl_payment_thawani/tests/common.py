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


class ThawaniCommon(PaymentCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.thawani = cls._prepare_provider('thawani', update_values={
            'thawani_secret_key': 'dummy',
            'thawani_publishable_key': 'dummy',
        })
        cls.provider = cls.thawani
        cls.currency = cls.currency_euro
        cls.notification_data = {
            'ref': cls.reference,
            'id': 'checkout_N3J5WVClUR0yunTkuXQ4sJV4YVKbeMmptpwK7qyXOhnVvZcOSY',
        }
