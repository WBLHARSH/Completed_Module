from odoo import fields, models, api


class ConfirmStockSms(models.TransientModel):
    _name = 'confirm.stock.sms'  # Correct inheritance to avoid changing the model name

    pick_ids = fields.Many2many('stock.picking', 'stock_picking_sms_rel')

    def send_sms(self):
        self.ensure_one()
        for company in self.pick_ids.company_id:
            if not company.has_received_warning_stock_sms:
                company.sudo().write({'has_received_warning_stock_sms': True})
        pickings_to_validate = self.env['stock.picking'].browse(self.env.context.get('button_validate_picking_ids'))
        return pickings_to_validate.button_validate()

    def dont_send_sms(self):
        self.ensure_one()
        for company in self.pick_ids.company_id:
            if not company.has_received_warning_stock_sms:
                company.sudo().write({
                    'has_received_warning_stock_sms': True,
                    'stock_move_sms_validation': False,
                })
        pickings_to_validate = self.env['stock.picking'].browse(self.env.context.get('button_validate_picking_ids'))
        return pickings_to_validate.button_validate()
