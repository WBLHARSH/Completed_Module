from odoo import models, api
from odoo.tools.float_utils import float_compare
from odoo.tools.misc import groupby


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _assign_picking(self):
        """Assign moves to pickings, grouping by seller_id, and create a single picking per seller."""
        Picking = self.env['stock.picking']

        grouped_moves = groupby(self, key=lambda m: m._key_assign_picking())
        for group, moves in grouped_moves:
            moves = self.env['stock.move'].concat(*moves)
            moves = moves.filtered(
                lambda m: float_compare(
                    m.product_uom_qty, 0.0, precision_rounding=m.product_uom.rounding
                ) >= 0
            )

            if not moves:
                continue

            # Group moves by seller_id
            seller_moves = {}
            for move in moves:
                seller_product = self.env['mp.seller.product'].sudo().search(
                    [('product_id', '=', move.product_id.id)], limit=1
                )
                seller_id = seller_product.seller_id.id if seller_product else False
                if seller_id not in seller_moves:
                    seller_moves[seller_id] = self.env['stock.move']
                seller_moves[seller_id] |= move

            # Create a single picking for each seller
            for seller_id, seller_moves_group in seller_moves.items():
                # Check if there's an existing picking for this seller and group
                existing_picking = Picking.search([
                    ('seller_id', '=', seller_id),
                    ('state', '=', 'draft'),
                    ('picking_type_id', '=', seller_moves_group[0].picking_type_id.id)
                ], limit=1)

                if existing_picking:
                    # Assign moves to the existing picking
                    seller_moves_group.write({'picking_id': existing_picking.id})
                else:
                    # Create a new picking for this seller
                    picking_values = seller_moves_group._get_new_picking_values()
                    picking_values[0]['seller_id'] = seller_id
                    new_picking = Picking.create(picking_values[0])
                    seller_moves_group.write({'picking_id': new_picking.id})

                seller_moves_group._assign_picking_post_process(new=not bool(existing_picking))

        return True

    def _get_new_picking_values(self):
        """Return create values for new pickings, one for each seller group."""
        picking_values_list = []
        origins = self.filtered(lambda m: m.origin).mapped('origin')
        origins = list(dict.fromkeys(origins))

        if len(origins) == 0:
            origin = False
        else:
            origin = ','.join(origins[:5])
            if len(origins) > 5:
                origin += "..."

        # Collect picking values for all moves
        picking_values = {
            'origin': origin,
            'company_id': self[0].company_id.id if self[0].company_id else False,
            'user_id': False,  # Set as required
            'move_type': self[0].group_id.move_type or 'direct',
            'picking_type_id': self[0].picking_type_id.id if self[0].picking_type_id else False,
            'location_id': self[0].location_id.id if self[0].location_id else False,
            "partner_id": self[0].partner_id.id,
            'location_dest_id': self[0].location_dest_id.id if self[0].location_dest_id else False,
        }
        picking_values_list.append(picking_values)
        return picking_values_list
