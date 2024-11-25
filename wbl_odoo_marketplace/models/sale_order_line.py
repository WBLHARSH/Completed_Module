from odoo import models, fields, api
from odoo.http import request


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    user_id = fields.Many2one(comodel_name='res.users', string='User')
    seller_id = fields.Many2one(comodel_name='marketplace.seller', string='Seller')
    image_1920 = fields.Image(related='product_id.image_1920', string='Image')
    sale_order_date = fields.Datetime(related='order_id.date_order', string='Order Date')
    delivery_count = fields.Integer(string='Delivery Orders',
                                    compute='_compute_delivery_count')
    partner_display_address = fields.Char(
        string="Customer",
        compute="_compute_partner_display_address",
    )
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

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)
    seller_amount = fields.Monetary(string="Seller Amount", currency_field='currency_id')
    admin_commission = fields.Monetary(string="Admin Commission", currency_field='currency_id')

    def _expand_states(self, states, domain, order):
        return [key for key, val in self._fields['mp_state'].selection]

    @api.model
    def create(self, vals):
        # Create the sale order line using the standard create method
        sale_order_line = super(SaleOrderLine, self).create(vals)

        # Access the computed fields after the record is created
        price_total = sale_order_line.price_total

        # Check if the product is defined and get the related seller
        if sale_order_line.product_id:
            seller_product = self.env['mp.seller.product'].sudo().search(
                [('product_id', '=', sale_order_line.product_id.id)], limit=1)

            if seller_product:
                seller_id = seller_product.seller_id
                user_id = seller_id.user_id

                # Update seller and user information
                sale_order_line.seller_id = seller_id.id
                sale_order_line.user_id = user_id.id if user_id else False

                # Calculate commission
                admin_commission = self._calculate_commission(price_total)
                sale_order_line.admin_commission = admin_commission
                sale_order_line.seller_amount = price_total - admin_commission

        return sale_order_line

    def _compute_partner_display_address(self):
        for line in self:
            partner = line.order_partner_id
            if partner:
                line.partner_display_address = f"{partner.name}\n{partner.street or ''} {partner.street2 or ''}\n{partner.city or ''} {partner.state_id.name or ''} {partner.zip or ''}\n{partner.country_id.name or ''}"
            else:
                line.partner_display_address = ''

    def _calculate_commission(self, price_total):
        if price_total:
            config_param = request.env['ir.config_parameter'].sudo()
            commission = config_param.get_param('wbl_odoo_marketplace.commission')
            admin_commission = float(price_total) * float(commission)
            return admin_commission

    @api.depends('order_id')
    def _compute_delivery_count(self):
        # Fetch pickings for these orders in a single query
        pickings = self.env['stock.picking'].sudo().search([
            ('seller_id', '=', self.seller_id.id),
            ('sale_id', '=', self.order_id.id)
        ])

        for line in self:
            line.delivery_count = len(pickings)

    def action_order_approved(self):
        for rec in self:
            rec.mp_state = 'approved'

    def action_order_denied(self):
        for rec in self:
            rec.mp_state = 'denied'

    def action_order_line_view_picking(self):
        self.ensure_one()
        # Search for stock pickings related to this seller and specific product
        pickings = self.env['stock.picking'].sudo().search([
            ('seller_id', '=', self.seller_id.id),
            ('sale_id', '=', self.order_id.id)
        ])

        if not pickings:
            return {'type': 'ir.actions.act_window_close'}

        # If there is only one picking, open the form view directly
        if len(pickings) == 1:
            action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pickings.id
        else:
            # If there are multiple pickings, open the tree view
            action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
            action['domain'] = [('id', 'in', pickings.ids)]

        return action
