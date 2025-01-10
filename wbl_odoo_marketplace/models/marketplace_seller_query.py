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

from odoo import fields, models


class MarketplaceSellerQuery(models.Model):
    _name = 'marketplace.seller.query'
    _description = "Marketplace Seller Query"
    _order = 'create_date desc'

    partner_id = fields.Many2one(comodel_name='res.partner')
    name = fields.Char(string='Name', required=True)
    contact_info = fields.Char(string='Email', required=True)
    topic = fields.Char(string='Topic', required=True)
    message = fields.Text(string='Message', required=True)
    user_id = fields.Many2one(comodel_name='res.users')
    state = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
        ],
        string='Status',
        required=True,
        readonly=True,
        copy=False,
        group_expand='_expand_states',
        default='pending',
    )

    def _expand_states(self, states, domain, order):
        return [key for key, val in self._fields['state'].selection]



    def action_sent_mail_to_seller_wizard(self):
        res = {
            'type': 'ir.actions.act_window',
            'name': 'Seller Query Mail Form',
            'res_model': 'seller.query.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_subject': self.topic,
                'default_email': self.contact_info,
                'default_mp_seller_query': self.id,
                'default_user_id': self.user_id.id,
                'default_query_from': 'customer_query',
            }
        }
        return res
