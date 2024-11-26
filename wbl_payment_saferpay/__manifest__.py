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


{
    'name': 'Saferpay Payment Provider with Refund',
    'version': '18.0.1.0.0',
    'summary': """Saferpay Odoo integration Multi currency payments Saferpay payment gateway Safer pay payment Saferpay payment acquirer Secured transaction processing Trusted payment gateway Saferpay eCommerce""",
    'description': """Saferpay Odoo integration Multi currency payments Saferpay payment gateway Safer pay payment Saferpay payment acquirer Secured transaction processing Trusted payment gateway Saferpay eCommerce""",
    'category': 'Accounting/Payment Providers',
    'author': 'Weblytic Labs',
    'company': 'Weblytic Labs',
    'website': "https://store.weblyticlabs.com",
    # 'price': 31,
    # 'currency': 'USD',
    'depends': ['base', 'payment', 'website', 'website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_saferpay_template.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
        'views/payment_provider_view.xml',
        'views/payment_transaction_views.xml',
        'wizard/account_payment_view.xml',
        'views/refund_button.xml',
    ],

    'license': 'OPL-1',
    'installable': True,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'auto_install': False,
    'application': True,
}
