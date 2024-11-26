from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    can_be_preorder = fields.Boolean(string="Can Be Preorder", default=False)
    override_default_preorder_configration = fields.Boolean(string="Override Default Preorder Configration",
                                                            default=False)
    minimum_qty_per_customer = fields.Integer(string="Minimum Quantity Per Customer")
    maximum_qty_per_customer = fields.Integer(string="Maximum Quantity Per Customer")
    total_preorder_booking_qty = fields.Integer(string="Total Preorder Booking Quantity")
    available_date = fields.Date(string="Available Date")
    preorder_payment_type = fields.Selection(
        selection=[('Full payment', 'full payment'), ('Partial payment', 'partial payment'),
                   ('Dynamic payment', 'dynamic payment')], string="Preorder Payment Type")
    deposit_amount = fields.Float(string='Deposit Amount')
    preorder_when_qty_less_than_or_equal = fields.Integer(string="Allow Preorder When Quantity Less Than Or Equal")
    preorder_policy_on_product = fields.Html(string="Preorder Policy On Product")

    @api.onchange('override_default_preorder_configration')
    def _onchange_override_default_preorder_configration(self):
        if self.override_default_preorder_configration:
            settings = self.env['res.config.settings'].sudo().get_values()
            self.minimum_qty_per_customer = settings.get('minimum_purchase_qty')
            self.maximum_qty_per_customer = settings.get('maximum_purchase_qty')
            self.total_preorder_booking_qty = settings.get('total_preorder_booking_qty')
            self.available_date = settings.get('available_date')
            self.preorder_payment_type = settings.get('preorder_payment_type')
            self.deposit_amount = settings.get('deposit_amount')
            self.preorder_when_qty_less_than_or_equal = settings.get('preorder_when_qty_less_than_or_equal')
            self.preorder_policy_on_product = settings.get('preorder_policy_on_product')
