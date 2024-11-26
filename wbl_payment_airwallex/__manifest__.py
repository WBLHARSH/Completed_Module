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
    'name': 'Airwallex Payment Gateway',
    'version': '17.0.1.0.0',
    'sequence': '-1',
    'summary': """AirWallex payment method
                    Multi-currency payment processing
                    Airwallex payment gateway integration
                    Refund functionality
                    Airwallex payment support
                    Odoo payment provider
                """,
    'description': """AirWallex payment method
                        Multi-currency payment processing
                        Airwallex payment gateway integration
                        Refund functionality
                        Airwallex payment support
                        Odoo payment provider
                        """,
    'category': 'Accounting/Payment Providers',
    'author': 'Weblytic Labs',
    'company': 'Weblytic Labs',
    'website': "https://store.weblyticlabs.com",
    'price': 31,
    'currency': 'USD',
    'depends': ['base', 'payment', 'website', 'website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_airwallex_templates.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
        'views/payment_provider_views.xml',
        'views/payment_transaction_views.xml',
        'wizard/account_payment_view.xml',
        'views/refund_button.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wbl_payment_airwallex/static/src/js/payment.js',
            'wbl_payment_airwallex/static/src/js/payment_airwallex_mixin.js',
        ],
    },
    'images': ['static/description/banner.gif'],
    'license': 'OPL-1',
    'installable': True,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'auto_install': False,
    'application': True,
}
