from odoo import models, fields, api
from odoo.exceptions import UserError


class PartnerNotification(models.Model):
    _name = 'notify.details'
    _description = 'Notify Details'

    partner_id = fields.Many2one('res.partner', string='Partner Detail', ondelete='cascade')
    product_id = fields.Many2one('product.template', string='Product Detail', ondelete='cascade')
    Name = fields.Char(string="Partner Name")
    email = fields.Char(string="Partner Email")
    phone = fields.Char(string="Partner Phone Number")
    comment = fields.Text(string="Comment Text")
    available_date = fields.Date(string='Available Date')

    @api.model
    def create(self, vals):
        product_id = vals.get('product_id')
        if product_id:
            product = self.env['product.template'].search(
                [('id', '=', product_id)])
            if not product.exists():
                raise UserError(f"Product with ID {product_id} does not exist.")
            vals['available_date'] = product.available_date
        return super(PartnerNotification, self).create(vals)

    @api.model
    def _send_notification_emails(self):
        today = fields.Date.today()
        notifications = self.search([('available_date', '=', today)])
        print(notifications)
        template = self.env.ref('wbl_website_preorder.email_template_notify_details')
        for notification in notifications:
            if template:
                template.send_mail(notification.id, force_send=True)
