from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        # Call the super method to retain the default functionality of action_confirm
        result = super(SaleOrder, self).action_confirm()

        # Iterate through each sale order
        for order in self:
            # Iterate through the order lines of the sale order
            for line in order.order_line:
                # Update the mp_state field to 'pending'
                line.mp_state = 'pending'

        return result
