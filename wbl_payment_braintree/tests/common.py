from odoo.addons.payment.tests.common import PaymentCommon


class BraintreeCommon(PaymentCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.braintree = cls._prepare_provider('braintree', update_values={
            'braintree_merchant_id': 'dummy',
            'braintree_public_key': 'dummy',
            'braintree_private_key': 'dummy',
        })
        cls.provider = cls.braintree
        cls.currency = cls.currency_euro

        cls.notification_data = {
            'ref': cls.reference,
            'id': 'tr_ABCxyz0123',
        }
