{
    'name': "Braintree Payment Gateway",
    'version': '17.0.0.1',
    'category': 'Accounting/Payment Providers',
    'sequence': -1,
    'summary': "Braintree Payment Gateway Plugin allows merchants to accept PayNow QR, Cards, Apple Pay, Google Pay, WeChatPay, AliPay and GrabPay Payments.",
    'author': 'Braintree Payment Solutions Pte Ltd',
    'website': 'https://www.braintree.com',
    'depends': ['payment', 'website', 'website_sale'],
    'data': [
        'views/payment_braintree_templates.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
        'views/payment_provider_views.xml',
        'views/payment_transaction_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wbl_payment_braintree/static/src/js/payment.js',
            'wbl_payment_braintree/static/src/js/test.js',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'application': True,
    'installable': True,
}
