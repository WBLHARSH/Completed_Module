from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    initial_balance_to_pay_before = fields.Float(string="Initial Balance to Pay Before", readonly=True)
    can_be_preorder = fields.Boolean(string="Can Be Preorder", compute='_compute_can_be_preorder', store=True)
    preorder_record = fields.Integer(string='Preorder Table')
    post_payment = fields.Boolean(string="post_payment", default=False)
    payment_type = fields.Char(string='Payment Type', default='full')

    @api.constrains('product_uom_qty')
    def check_installment_quantity(self):
        for line in self:
            if line.name == "[PayInstallment_012] Installment" and line.product_uom_qty > 1:
                message = "Installment can be paid one by one only"
                raise ValidationError(message)

    @api.depends('product_id')
    def _compute_can_be_preorder(self):
        for line in self:
            line.can_be_preorder = line.product_id.product_tmpl_id.can_be_preorder
