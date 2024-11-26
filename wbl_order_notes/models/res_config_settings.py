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

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    website = fields.Many2one('website', string="Website", ondelete='cascade', required=True,
                              index=True)
    enable_order_message_field = fields.Boolean(string='Enable Order Message Field')
    enable_desire_date_field = fields.Boolean(string='Enable Desirable Date Field')
    maximum_number_of_days = fields.Integer(string="Maximum Number Of Days")
    minimum_number_of_days = fields.Integer(string="Minimum Number Of Days")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config_parameter_sudo = self.env['ir.config_parameter'].sudo()
        website_id = ir_config_parameter_sudo.get_param('website.website', default="1")
        res.update(
            website=int(website_id),
            enable_order_message_field=ir_config_parameter_sudo.get_param('website.enable_order_message_field',
                                                                        default=False),
            enable_desire_date_field=ir_config_parameter_sudo.get_param('website.enable_desire_date_field',
                                                                        default=False),
            maximum_number_of_days=int(ir_config_parameter_sudo.get_param('website.maximum_number_of_days', default=0)),
            minimum_number_of_days=int(ir_config_parameter_sudo.get_param('website.minimum_number_of_days', default=0)),
        )
        return res

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config_parameter = self.env['ir.config_parameter'].sudo()
        ir_config_parameter.set_param('website.website', self.website.id if self.website else 0)
        ir_config_parameter.set_param('website.enable_order_message_field', self.enable_order_message_field)
        ir_config_parameter.set_param('website.enable_desire_date_field', self.enable_desire_date_field)
        ir_config_parameter.set_param('website.maximum_number_of_days', self.maximum_number_of_days)
        ir_config_parameter.set_param('website.minimum_number_of_days', self.minimum_number_of_days)
