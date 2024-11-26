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
    'name': 'Shipping Cost by Distance',
    'version': '17.0.1.0.0',
    'description': """Shipping Cost by Distance""",
    'summary': """Shipping Cost by Distance""",
    'category': 'eCommerce',
    'author': 'Weblytic Labs',
    'company': 'Weblytic Labs',
    'website': 'https://store.weblyticlabs.com',
    'price': 31,
    'currency': 'USD',
    'depends': ['base', 'mail', 'website', 'delivery', 'website_payment', 'website_sale', 'payment', 'sale_management',
                'stock', 'website_google_map'],
    'data': [
        'views/res_config_settings_view.xml',
        'views/delivery_price_rule_view.xml'
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
}
