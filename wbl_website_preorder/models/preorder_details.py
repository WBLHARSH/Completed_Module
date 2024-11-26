from odoo import models, fields, api


class ProductPreorder(models.Model):
    _name = 'product.preorder'
    _description = 'Product Preorder'

    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line', required=True, ondelete='cascade')
    payment_type = fields.Char(string="Payment Type")
    total_amount = fields.Char(string="Total Amount")
    remaining_amount = fields.Char(string="Remaining Amount")
    paid_amount = fields.Char(string="Paid Amount")
    status = fields.Selection(selection=[('paid', 'Paid'), ('remaining', 'Remaining')])
    sale_order_line_name = fields.Text(string='Sale Order Line Name', related='sale_order_line_id.name', store=True)
    sale_order_id = fields.Many2one(related='sale_order_line_id.order_id', string='Sale Order', store=True)
    partner_id = fields.Many2one('res.partner', ondelete='cascade', string='Partner Id')
