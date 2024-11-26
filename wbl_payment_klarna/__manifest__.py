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
    'name': 'Klarna Payment Gateway',
    'version': '18.0.1.0.0',
    'summary': """Klarna payment Odoo Klarna integration Secure payments Klarna setup Payment acquirer Easy Klarna configuration Stripe Klarna payment provider""",
    'description': """Klarna payment Odoo Klarna integration Secure payments Klarna setup Payment acquirer Easy Klarna configuration Stripe Klarna payment provider""",
    'category': 'Accounting/Payment Providers',
    'author': 'Weblytic Labs',
    'company': 'Weblytic Labs',
    'website': "https://store.weblyticlabs.com",
    # 'price': 31,
    # 'currency': 'USD',
    'depends': ['base', 'payment', 'website', 'website_sale'],
    'data': [
        'views/payment_klarna_templates.xml',
        'views/_klarna_payment_template_.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
        'views/payment_provider_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wbl_payment_klarna/static/src/js/klarna.js',
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
