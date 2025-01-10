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
    'name': 'Hyperpay Payment Provider with Refund',
    'version': '17.0.1.0.0',
    'summary': """HyperPay payment gateway integration Online payment processing Odoo Refund management HyperPay Secure payment options Odoo HyperPay Payment Acquirer for Odoo Website""",
    'description': """HyperPay payment gateway integration Online payment processing Odoo Refund management HyperPay Secure payment options Odoo HyperPay Payment Acquirer for Odoo Website""",
    'category': 'Sales',
    'author': 'Weblytic Labs',
    'company': 'Weblytic Labs',
    'website': "https://store.weblyticlabs.com",
    'price': '65.00',
    'currency': 'USD',
    'depends': ['base', 'payment', 'website', 'website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_hyperpay_template.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
        'views/payment_provider_view.xml',
        'views/payment_transaction_views.xml',
        'wizard/account_payment_view.xml',
        'views/refund_button.xml',
    ],
    'images': ['static/description/banner.gif'],
    'live_test_url': 'https://youtu.be/JV7pF4N6PhM',
    'license': 'OPL-1',
    'installable': True,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'auto_install': False,
    'application': True,
}
