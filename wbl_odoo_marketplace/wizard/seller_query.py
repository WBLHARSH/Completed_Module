from odoo import models, fields, api, _
from odoo.http import request
from odoo.exceptions import UserError
from bs4 import BeautifulSoup


class SellerQueryWizard(models.TransientModel):
    _name = 'seller.query.wizard'

    subject = fields.Char(string="Subject")
    partner_id = fields.Many2one(comodel_name='res.partner')
    email = fields.Char(string="Email")
    message = fields.Text(string="Message")
    name = fields.Char(string='Name')
    mp_seller_query = fields.Many2one('marketplace.seller.query', string='Marketplace Seller Query')
    mp_customer_query = fields.Many2one('marketplace.customer.query', string='Marketplace Customer Query')
    user_id = fields.Many2one(comodel_name='res.users')
    body = fields.Html(string="Contents", sanitize_style=True, readonly=False, store=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', 'seller_query_wizard_ir_attachment_rel',
        'wizard_id', 'attachment_id', string='Attachments', readonly=False, store=True)
    query_from = fields.Selection(
        selection=[('customer_query', 'Customer Query'), ('complete', 'Completed'), ('close', 'closed')],
        string='Query From'
    )

    def action_sent_mail_to_seller(self):
        if not self._is_body_valid(self.body) or not self.subject:
            raise UserError(_("Please provide both a subject and a message to send the mail."))

        # Reference the email template
        template = self.env.ref('wbl_odoo_marketplace.admin_sent_mail_to_seller_for_seller_query_template')
        if not template:
            raise UserError(_("The email template could not be found. Please check the template configuration."))

        # Prepare email context with attachments
        email_ctx = {
            'default_attachment_ids': [(4, attachment.id) for attachment in self.attachment_ids],
        }

        # Generate mail from the template
        mail_id = template.with_context(email_ctx).send_mail(self.id, force_send=False)
        if not mail_id:
            raise UserError(_("The mail could not be created. Please check your configuration."))

        # Attach files directly to the mail
        mail = self.env['mail.mail'].browse(mail_id)
        if mail.exists():
            mail.attachment_ids = [(4, attachment.id) for attachment in self.attachment_ids]
            mail.send()
        else:
            raise UserError(_("Mail record not found after creation. Please try again."))

        # Update the query state
        if self.query_from == 'customer_query':
            self.mp_seller_query.state = 'approved'
        elif self.query_from == 'complete':
            self.mp_customer_query.state = 'opened'
        elif self.query_from == 'close':
            self.mp_customer_query.state = 'closed'

    @staticmethod
    def _is_body_valid(html_content):
        if not html_content:
            return False
        soup = BeautifulSoup(html_content, 'html.parser')
        return bool(soup.get_text(strip=True))
