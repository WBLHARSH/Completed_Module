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
    'name': 'Payfast Payment Acquirer',
    'version': '18.0.1.0.0',
    'summary': """
        Payfast Payment Gateway Payment Integration Credit Card Payment Gateway Invoicing with Payfast EFT Payment PCI DSS Compliant Payfast Payment Method Payfast payment acquirer Payfast for Odoo South Africa Payfast
    """,
    'description': """
        Payfast Payment Gateway Payment Integration Credit Card Payment Gateway Invoicing with Payfast EFT Payment PCI DSS Compliant Payfast Payment Method Payfast payment acquirer Payfast for Odoo South Africa Payfast
    """,
    'category': 'Sales',
    'author': 'Weblytic Labs',
    'company': 'Weblytic Labs',
    'website': "https://store.weblyticlabs.com",
    'price': 31,
    'currency': 'USD',
    'depends': ['base', 'payment', 'website', 'website_sale'],
    'data': [
        'views/payment_payfast_templates.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
        'views/payment_provider_views.xml',
        'views/payment_transaction_views.xml',
    ],
    'images': ['static/description/banner.gif'],
    'live_test_url': 'https://youtu.be/QmSm4Kpe554',
    'license': 'OPL-1',
    'installable': True,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'auto_install': False,
    'application': True,
}
