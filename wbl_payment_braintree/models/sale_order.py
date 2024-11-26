from odoo import models, fields
from odoo.addons.test_convert.tests.test_convert import Field


class SaleOrder(models.Model):
    _inherit = "sale.order"

    braintree_txn_id = fields.Char(string='Braintree Transaction Id')
    braintree_payment_currency = fields.Char(string='Braintree Payment Currency')
    braintree_txn_status = fields.Char(string='Braintree Transaction Status')
