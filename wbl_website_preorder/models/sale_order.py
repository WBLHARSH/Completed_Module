from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"
    customised_products = fields.Char(string="customized products")
    dynamic_amount = fields.Integer(string="Dynamic Amount")
    dynamic_fix_amount = fields.Integer(string="Dynamic Fix Amount")

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        for line in order.order_line:
            if line.product_id.product_tmpl_id.can_be_preorder:
                line.can_be_preorder = True
        return order

    def _cart_update(self, product_id, line_id=None, add_qty=0, set_qty=0, **kwargs):
        response = super(SaleOrder, self)._cart_update(product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty,
                                                       **kwargs)
        product = self.env['product.product'].browse(product_id)
        post_payment = kwargs.get('price_unit')
        preorder_order_id = kwargs.get('preorder_order_id')
        remaining_amount = kwargs.get('remaining_amount')
        payment_type = self.customised_products
        dynamic_amount = self.dynamic_amount
        line_id = response['line_id']

        # ----------------------------- Installment -----------------------------------------------
        if post_payment and preorder_order_id:
            self.order_line.filtered(lambda l: l.product_id.id == product_id).write(
                {'price_unit': remaining_amount, 'post_payment': True, 'preorder_record': preorder_order_id})

        # ----------------------------- Full Payment -----------------------------------------------
        if payment_type == 'full' or product.product_tmpl_id.preorder_payment_type == "Full payment":
            self._apply_full_payment(line_id)

        # ----------------------------- Dynamic Payment -----------------------------------------------
        if dynamic_amount and product.product_tmpl_id.preorder_payment_type == "Dynamic payment":
            self._apply_dynamic_payment_logic(line_id, dynamic_amount)

        # ----------------------------- Partial Payment -----------------------------------------------
        if payment_type == 'partial' and product.product_tmpl_id.preorder_payment_type == "Partial payment":
            self._apply_partial_payment(line_id, product)
        return response

    # ----------------------------- Partial Payment -----------------------------------------------
    def _apply_partial_payment(self, sale_order_line_id, product):
        sale_order_line = self.env['sale.order.line'].browse(sale_order_line_id)
        if not sale_order_line:
            return  # Add error handling if needed

        deposit_amount = product.product_tmpl_id.deposit_amount or 0
        list_price = product.lst_price or 0
        balance_to_pay_before = (list_price * deposit_amount / 100)
        sale_order_line.write({
            'price_unit': balance_to_pay_before,
            'initial_balance_to_pay_before': balance_to_pay_before
        })

    # ----------------------------- Full Payment -----------------------------------------------
    def _apply_full_payment(self, line_id):
        pass

    # ----------------------------- Dynamic Payment -----------------------------------------------
    def _apply_dynamic_payment_logic(self, line_id, dynamic_amount):
        try:
            sale_order_line = self.env['sale.order.line'].browse(line_id)
            sale_order_line.write({'price_unit': dynamic_amount})
        except Exception as e:
            print(f"Error in _apply_dynamic_payment_logic: {e}")
