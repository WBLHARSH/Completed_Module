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

from odoo import fields, models, api


class MarketplaceCustomerQuery(models.Model):
    _name = 'marketplace.customer.query'
    _description = "Marketplace Customer Query"
    _order = 'create_date desc'

    partner_id = fields.Many2one(comodel_name='res.partner', required=True)
    seller_id = fields.Many2one(comodel_name='marketplace.seller', string='Seller', required=True)
    seller_uid = fields.Many2one(comodel_name='res.users', string='User', required=True)
    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone', required=True)
    subject = fields.Char(string='Subject', required=True)
    question = fields.Text(string='Question', required=True)
    state = fields.Selection(
        selection=[
            ('processing', 'Processing'),
            ('opened', 'Opened'),
            ('closed', 'Closed'),
        ],
        string='Status',
        required=True,
        default='processing',
    )

    def action_sent_mail_to_customer_wizard(self):
        res = {
            'type': 'ir.actions.act_window',
            'name': 'Seller Query Mail Form',
            'res_model': 'seller.query.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_subject': self.subject,
                'default_email': self.email,
                'default_mp_customer_query': self.id,
                'default_user_id': self.seller_uid.id,
                'default_partner_id': self.partner_id.id,
                'default_name': self.name,
                'default_query_from': 'complete',
            }
        }
        return res

    def action_sent_mail_to_customer_close_wizard(self):
        res = {
            'type': 'ir.actions.act_window',
            'name': 'Seller Query Mail Form',
            'res_model': 'seller.query.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_subject': self.subject,
                'default_email': self.email,
                'default_mp_customer_query': self.id,
                'default_user_id': self.seller_uid.id,
                'default_partner_id': self.partner_id.id,
                'default_name': self.name,
                'default_query_from': 'close',
            }
        }
        return res