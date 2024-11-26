# -*- coding: utf-8 -*-
#
#################################################################################
# Author      : Weblytic Labs Pvt. Ltd. (<https://store.weblyticlabs.com/>)
# Copyright(c): 2023-Present Weblytic Labs Pvt. Ltd.
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
##################################################################################

from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"

    distance_amount = fields.Char(string="Distance Amount")

    def _cart_update(self, product_id, line_id=None, add_qty=0, set_qty=0, **kwargs):
        # Perform the default cart update logic
        response = super(SaleOrder, self)._cart_update(product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty,
                                                       **kwargs)

        # Ensure add_qty is not None and set to 0 if it is
        add_qty = add_qty or 0

        # Call reset_distance_amount_if_empty after updating the cart
        self.reset_distance_amount_if_empty()

        # Call a method to handle logic when a new product is added
        self._update_distance_amount_on_add_product(add_qty)

        return response

    def reset_distance_amount_if_empty(self):
        """Set distance_amount to an empty string if there are no items in the cart."""
        if not self.order_line:
            self.distance_amount = ''

    def _update_distance_amount_on_add_product(self, add_qty):
        """Update the distance_amount when a new product is added."""
        if add_qty > 0:
            # Update the distance_amount as per your business logic
            self.distance_amount = ''  # Replace with actual logic to calculate the amount
