from odoo import api, fields, models, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_multi_currency = fields.Boolean(string="Enable Multi Currency", default=False)
    currencies_ids = fields.Many2many(comodel_name='res.currency', string='Currencies')
