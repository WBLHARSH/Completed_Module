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
    'name': 'Website Product Brand',
    'version': '18.0.1.0.0',
    'summary': """Product brand management Custom brand pages Brand visibility on website Filter products by brand Brand awareness Manufacturer Data""",
    'description': """Product brand management Custom brand pages Brand visibility on website Filter products by brand Brand awareness Manufacturer Data""",
    'category': 'eCommerce',
    'author': 'Weblytic Labs',
    'company': 'Weblytic Labs',
    'website': "https://store.weblyticlabs.com",
    'depends': ['base', 'sale', 'website', 'website_sale'],
    'price': '25.00',
    'currency': 'USD',
    'data': [
        'security/ir.model.access.csv',
        'views/product_kanban_view.xml',
        'data/brand_data.xml',
        'views/brand_views.xml',
        'views/product_views.xml',
        'views/res_config_settings.xml',
        'views/templates.xml',
        'views/brand_templates.xml',
        'views/brand_items_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wbl_product_brand/static/src/js/brand.js',
            'wbl_product_brand/static/src/js/products.js',
            'wbl_product_brand/static/src/js/website_sale.js',
            'wbl_product_brand/static/src/js/pop.js',
            'wbl_product_brand/static/src/css/brand.css',
        ],
    },
    'images': ['static/description/banner.gif'],
    'live_test_url': 'https://youtu.be/umIXMktkpu4',
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
}
