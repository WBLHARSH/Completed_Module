from odoo.tests import tagged
from odoo.tools import mute_logger
from odoo.addons.payment.tests.http_common import PaymentHttpCommon
from odoo.addons.wbl_payment_braintree.tests.common import BraintreeCommon


@tagged('post_install', '-at_install')
class BraintreeTest(BraintreeCommon, PaymentHttpCommon):

    @mute_logger(
        'odoo.addons.payment_mollie.controllers.main',
        'odoo.addons.payment_mollie.models.payment_transaction',
    )
    def test_webhook_notification_confirms_transaction(self):
        """ Test the processing of a webhook notification. """
        tx = self._create_transaction('redirect')
        self.assertEqual(tx.state, 'done')
