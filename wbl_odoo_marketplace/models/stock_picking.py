from odoo import models, api, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    seller_id = fields.Many2one(comodel_name='marketplace.seller', string='Seller')
    mp_state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('denied', 'Denied'),
        ],
        string='Status',
        required=True,
        readonly=True,
        group_expand='_expand_states',
        copy=False,
        default='pending',
    )

    def _expand_states(self, states, domain, order):
        return [key for key, val in self._fields['mp_state'].selection]

    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        if res.seller_id:
            res.user_id = res.seller_id.user_id
        return res

    def action_order_approved(self):
        for rec in self:
            rec.mp_state = 'approved'

    def action_order_denied(self):
        for rec in self:
            rec.mp_state = 'denied'
