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
    'name': 'Multi Vendor Marketplace',
    'version': '17.0.1.0.0',
    'summary': """Ticket Booking System Reservation Management Software POS Ticketing System Movie Ticket Booking App Theater Seat Reservation Show Ticketing Software Event Booking System Dynamic Ticket Pricing Opera Ticket Reservation Show Booking Hotel Reservation POS Multi-Auditorium Management Event Management Software.""",
    'description': """Ticket Booking System Reservation Management Software POS Ticketing System Movie Ticket Booking App Theater Seat Reservation Show Ticketing Software Event Booking System Dynamic Ticket Pricing Opera Ticket Reservation Show Booking Hotel Reservation POS Multi-Auditorium Management Event Management Software.""",
    'category': 'eCommerce',
    'author': 'Weblytic Labs',
    'company': 'Weblytic Labs',
    'website': "https://store.weblyticlabs.com",
    'price': '125.00',
    'currency': 'USD',
    'depends': ['base', 'mail', 'portal', 'website', 'website_sale', 'account', 'sale_management', 'sale', 'board',
                'stock'],
    'data': [
        'data/ir_module_category_data.xml',
        'security/marketplace_security.xml',
        'security/ir.model.access.csv',
        'security/ir_rules.xml',
        'views/res_config_settings_views.xml',
        'views/marketplace_seller_views.xml',
        'views/marketplace_seller_payment_sequence.xml',
        'wizard/request_for_payment.xml',
        'wizard/pay_to_seller.xml',
        'wizard/seller_query_view.xml',
        'views/mp_seller_payment.xml',
        'views/mp_seller_delivery_order.xml',
        'views/mp_seller_order_views.xml',
        'views/seller_profile_views.xml',
        'views/seller_product_image_views.xml',
        'views/mp_seller_product_views.xml',
        'views/product_views.xml',
        'views/mp_seller_invoicing.xml',
        'views/customer_query_views.xml',
        'views/seller_query_views.xml',
        'views/marketplace_menus.xml',
        'data/data.xml',
        'data/mail_template_data.xml',
        'data/seller_payment_product.xml',
        'views/portal_templates.xml',
        'views/become_seller_templates.xml',
        'views/seller_templates.xml',
        'views/templates.xml',
        'views/seller_profile_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wbl_odoo_marketplace/static/src/js/seller_shop.js',
            'wbl_odoo_marketplace/static/src/js/seller_form.js',
            'wbl_odoo_marketplace/static/src/js/contact_seller_form.js',
            'wbl_odoo_marketplace/static/src/js/seller_product_search.js',
            'wbl_odoo_marketplace/static/src/js/seller_page.js',
            'wbl_odoo_marketplace/static/src/css/marketplace.css',
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
        ],
        'web.assets_backend': [
            'web/static/lib/owl/owl.js',  # Explicitly load Owl if necessary
            'wbl_odoo_marketplace/static/src/xml/marketplace_dashboard_template.xml',
            'wbl_odoo_marketplace/static/src/js/dashboard.js',
            'wbl_odoo_marketplace/static/src/js/chart_renderer/chart_renderer.js',
            'wbl_odoo_marketplace/static/src/js/chart_renderer/chart_renderer.xml',
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
        ],
    },
    'images': ['static/description/banner.gif'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
}
