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
    'name': 'Address Base Delivery Charge',
    'version': '17.0.1.0.0',
    'description': """Address Base Delivery Charge""",
    'summary': """Address Base Delivery Charge""",
    'category': 'eCommerce',
    'author': 'Weblytic Labs',
    'company': 'Weblytic Labs',
    'website': 'https://store.weblyticlabs.com',
    'depends': ['base', 'mail', 'website', 'delivery', 'website_payment', 'website_sale', 'payment', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/address_view.xml',
        'views/address_hide_view.xml',
        'views/delivery_view.xml',
        'views/sale_order_view.xml',
        'views/address_template_view.xml',
        'views/my_orders_view.xml',
        'views/portaLtemplate_view.xml',
        'views/add_address_in_potal_template_view.xml',
        'views/shop_payment_template.xml',
        'views/my_home_view.xml',
        'views/all_addresses_menu_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wbl_address_base_delivery_charge/static/src/js/address.js',
            'wbl_address_base_delivery_charge/static/src/js/portal.js',
            'wbl_address_base_delivery_charge/static/src/js/test.js',
        ],
    },
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
}
