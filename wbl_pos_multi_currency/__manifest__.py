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
    'name': 'POS Multi Currency',
    'version': '18.0.1.0.0',
    'sequence': -1,
    'summary': """ POS shipping Home Delivery POS Point-of-sale Home Delivery Method for Extra fee on home delivery for POS Home dispatch In-store to home delivery Retail POS delivery POS-to-home logistics Transparent delivery fees Delivery from store POS. """,
    'description': """ POS shipping Home Delivery POS Point-of-sale Home Delivery Method for Extra fee on home delivery for POS Home dispatch In-store to home delivery Retail POS delivery POS-to-home logistics Transparent delivery fees Delivery from store POS. """,
    'category': 'eCommerce',
    'author': 'Weblytic Labs',
    'company': 'Weblytic Labs',
    'website': "https://store.weblyticlabs.com",
    'depends': ['point_of_sale', 'web', 'account', 'website'],
    # 'images': ['static/description/banner.gif'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
    'data': [
        'views/res_config_settings_view.xml',
        'views/pos_payment_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'wbl_pos_multi_currency/static/src/js/payment_screen.js',
            'wbl_pos_multi_currency/static/src/js/multi_currency_popup.js',
            'wbl_pos_multi_currency/static/src/js/pos_payment.js',
            'wbl_pos_multi_currency/static/src/xml/multi_currency_button.xml',
        ],
    },
}
