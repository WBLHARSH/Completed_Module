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
    'name': 'Website Payment Extra Fee',
    'version': '17.0.1.0.0',
    'description': """Payment fee Website surcharge Extra payment fees Payment surcharge Minimum order amount fee Product-specific payment fees Additional charges on orders Custom fee rules Configurable payment fees Country-based surcharge Product extra fees Payment Method Surcharge""",
    'summary': """Payment fee Website surcharge Extra payment fees Payment surcharge Minimum order amount fee Product-specific payment fees Additional charges on orders Custom fee rules Configurable payment fees Country-based surcharge Product extra fees Payment Method Surcharge""",
    'category': 'eCommerce',
    'author': 'Weblytic Labs',
    'company': 'Weblytic Labs',
    'website': 'https://store.weblyticlabs.com',
    'price': '50.00',
    'currency': 'USD',
    'depends': ['base', 'mail', 'website', 'delivery', 'website_payment', 'website_sale', 'payment', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'data/payement_fee_product.xml',
        'views/payment_provider_view.xml',
        'views/payment_method_view.xml',
        'views/website_sale_template_view.xml',
        'views/payment_transaction_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wbl_payment_fee/static/src/js/payment_form.js',
        ],
    },
    'images': ['static/description/banner.gif'],
    'live_test_url': 'https://youtu.be/vgeP_Ga1u7Y',
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
}
