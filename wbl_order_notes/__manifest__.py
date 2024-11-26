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
    'name': 'Order Note',
    'summary': """odoo order notes project""",
    'description': """odoo order notes project""",
    'category': 'Sales',
    'author': 'Weblytic Labs',
    'company': 'Weblytic Labs',
    'website': "https://store.weblyticlabs.com",
    'depends': ['base', 'mail', 'website',"sale","website_sale", "payment"],  # Ensure 'website' is included if you are extending website settings
    'data': [
        'views/res_config_settings_views.xml',
        'views/website_sale_picking.xml',
    ],
    'assets': {
		'web.assets_frontend': [
			'wbl_order_notes/static/src/js/form_payment_desire_date.js',
			'wbl_order_notes/static/src/js/save_delivery.js',
		],
	},
    'license':'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
}
