from odoo import models, fields, _
from werkzeug import urls
import logging
from odoo.http import request
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    braintree_payment_status = fields.Char(string='Transaction Status', help='Braintree payment transaction status')
    braintree_transaction_id = fields.Char(string='Transaction ID', help='Braintree payment transaction id')
    braintree_payment_currency = fields.Char(string='Transaction Currency',
                                             help='Braintree payment transaction currency')

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'braintree':
            return res

        payment_result = self.send_payment()
        if payment_result:
            res.update({
                'braintree_transaction_id': payment_result.get('braintree_transaction_id'),
                'braintree_payment_status': payment_result.get('braintree_payment_status'),
            })

        # Define the redirect URL after successful payment processing
        base_url = self.provider_id.get_base_url()
        redirect_url = urls.url_join(base_url, '/payment/braintree/return')
        res.update({
            'api_url': redirect_url,
            'reference': self.reference,
        })
        return res

    def send_payment(self):
        order = request.website.sale_get_order()
        if not order:
            return {}
        if order.braintree_txn_id:
            self.braintree_transaction_id = order.braintree_txn_id
            self.braintree_payment_status = order.braintree_txn_status
            self.braintree_payment_currency = order.currency_id.name
            self.provider_reference = order.braintree_txn_id
            self._cr.commit()

            return {
                'braintree_transaction_id': order.braintree_txn_id,
                'braintree_payment_status': order.braintree_txn_status,
            }
        else:
            return {}

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'braintree' or len(tx) == 1:
            return tx

        reference = notification_data.get('reference')
        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'braintree')])
        if not tx:
            raise ValidationError(
                "Message: " + _("No transaction found matching reference %s.", reference)
            )
        return tx

    def _process_notification_data(self, notification_data):
        super()._process_notification_data(notification_data)
        if self.provider_code != 'braintree':
            return
        _logger.info(
            "validated cash on delivery payment for transaction with reference %s: set as pending",
            self.reference
        )
        self._set_done()
