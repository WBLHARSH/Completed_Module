from odoo import api, fields, models


class Paymentprovider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('braintree', "Braintree Payment Gateway")], ondelete={'braintree': 'set default'}
    )

    braintree_merchant_id = fields.Char(
        string="Merchant Id",
        required_if_provider='braintree')

    braintree_public_key = fields.Char(
        string="Public Key",
        required_if_provider='braintree')

    braintree_private_key = fields.Char(
        string="Private Key",
        required_if_provider='braintree')

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['braintree'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        return res
