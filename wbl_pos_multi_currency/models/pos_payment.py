from odoo import api, fields, models, _


class PosPayment(models.Model):
    _inherit = 'pos.payment'

    payment_currency = fields.Char(string='Payment Currency')
    currency_amount = fields.Float(string='Currency Amount')
    payment_symbol = fields.Char(string='Currency Amount')
