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
    'name': 'PayTabs Payment Gateway',
    'version': '17.0.1.0.0',
    'sequence': -4,
    'description': """Integrate PayTabs with Odoo PayTabs payment acquirer PayTabs payment gateway integration Refund functionality Odoo PayTabs Odoo payment processing solutions Multi-currency payments Odoo 3D Secure payment processing""",
    'summary': """Integrate PayTabs with Odoo PayTabs payment acquirer PayTabs payment gateway integration Refund functionality Odoo PayTabs Odoo payment processing solutions Multi-currency payments Odoo 3D Secure payment processing""",
    'category': 'eCommerce',
    'author': 'Weblytic Labs',
    'company': 'Weblytic Labs',
    'website': 'https://store.weblyticlabs.com',
    'price': 31,
    'currency': 'USD',
    'depends': ['base', 'mail', 'website', 'delivery', 'website_payment', 'website_sale', 'payment', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_paytabs_template.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
        'views/payment_provider_view.xml',
        'views/payment_transaction_views.xml',
        'wizard/account_payment_view.xml',
        'views/refund_button.xml',
    ],
    'images': ['static/description/banner.gif'],
    'license': 'OPL-1',
    'installable': True,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'auto_install': False,
    'application': True,
}
