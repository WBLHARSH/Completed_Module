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


class PayTabsCommon(PaymentCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.payTabs = cls._prepare_provider('payTabs', update_values={
            'moyasar_public_key': 'dummy',
            'moyasar_secret_key': 'dummy',
        })
        cls.provider = cls.payTabs
        cls.currency = cls.currency_euro
        cls.notification_data = {
            'ref': cls.reference,
            'id': 'fdff13af-fa07-486d-98ea-76ffdf8d7673',
        }
