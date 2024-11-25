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

from odoo import fields, models, api, _
from odoo.http import request
from odoo.exceptions import UserError


class MarketplaceSeller(models.Model):
    _name = 'marketplace.seller'
    _description = "Marketplace Seller"

    user_id = fields.Many2one(comodel_name='res.users')
    partner_id = fields.Many2one(comodel_name='res.partner', related='user_id.partner_id')
    name = fields.Char(string='Name')
    image_1920 = fields.Image(related='partner_id.image_1920', readonly=False)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile', related='partner_id.mobile', readonly=False)
    street = fields.Char(related='partner_id.street', readonly=False)
    street2 = fields.Char(related='partner_id.street2', readonly=False)
    city = fields.Char(related='partner_id.city', readonly=False)
    zip = fields.Char(related='partner_id.zip', readonly=False)
    vat = fields.Char(related='partner_id.vat', string="Tax ID", readonly=False)
    state_id = fields.Many2one(comodel_name="res.country.state", string='State', related='partner_id.state_id',
                               domain="[('country_id', '=?', country_id)]", readonly=False)
    country_id = fields.Many2one(comodel_name='res.country', string='Country')
    country_code = fields.Char(string="Country Code", related='country_id.code', readonly=False)
    shop_name = fields.Char(string="Shop Name")
    shop_url = fields.Char(string="Shop Url")
    shop_image_logo = fields.Image()
    shop_image_banner = fields.Image()
    description = fields.Text(string="Description")
    terms_conditions = fields.Html(string='Terms & Conditions')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('denied', 'Denied'),
        ],
        string='Status',
        required=True,
        readonly=True,
        copy=False,
        group_expand='_expand_states',
        default='draft',
    )

    def _expand_states(self, states, domain, order):
        return [key for key, val in self._fields['state'].selection]

    def _get_action_view_seller(self):
        action = self.env["ir.actions.actions"]._for_xml_id("wbl_odoo_marketplace.action_mp_seller_profile")
        action['res_id'] = self.env['marketplace.seller'].sudo().search([('user_id', '=', self._uid)]).id
        return action

    def action_approval_request(self):
        for rec in self:
            rec.state = 'pending'

    def action_seller_approved(self):
        group_id = self.env.ref('wbl_odoo_marketplace.group_marketplace_seller')
        for rec in self:
            rec.state = 'approved'
            self.user_id.write({'groups_id': [(4, group_id.id)]})
            self._send_seller_status_notification(rec.id, 'Approved')

    def action_seller_denied(self):
        for rec in self:
            rec.state = 'denied'
            self._send_seller_status_notification(rec.id, "Denied")

    def _send_seller_status_notification(self, seller_id, status):
        config_param = request.env['ir.config_parameter'].sudo()
        notify_seller_on_approval = config_param.get_param('wbl_odoo_marketplace.seller_approved_notify_to_seller')
        notify_admin_on_denial = config_param.get_param('wbl_odoo_marketplace.seller_denied_notify_to_admin')

        if status == "Approved" and notify_seller_on_approval:
            template = request.env.ref('wbl_odoo_marketplace.mail_template_seller_request_approved')
            template.send_mail(seller_id, force_send=True)
        elif status == "Denied" and notify_admin_on_denial:
            template = request.env.ref('wbl_odoo_marketplace.mail_template_seller_request_denied')
            template.send_mail(seller_id, force_send=True)

