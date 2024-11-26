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

    abidjans = fields.Many2many('abidjan', string="Abidjans", ondelete='cascade')
    ivory_coast = fields.Many2many('ivory.coast', string="Ivory Coasts", ondelete='cascade')
    countries = fields.Many2many('country.details', string="Countries", ondelete='cascade')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrConfigParam = self.env['ir.config_parameter'].sudo()

        abidjans_ids = IrConfigParam.get_param('res.config.settings.abidjans', default='')
        ivory_coast_ids = IrConfigParam.get_param('res.config.settings.ivory_coast', default='')
        countries_ids = IrConfigParam.get_param('res.config.settings.countries', default='')

        # Handle abidjans safely, only include records that exist
        abidjans = self.env['abidjan'].browse([int(id) for id in abidjans_ids.split(',') if id])
        abidjans = abidjans.exists() if abidjans else False

        # Handle ivory_coast safely, only include records that exist
        ivory_coast = self.env['ivory.coast'].browse([int(id) for id in ivory_coast_ids.split(',') if id])
        ivory_coast = ivory_coast.exists() if ivory_coast else False

        # Handle countries safely, only include records that exist
        countries = self.env['country.details'].browse([int(id) for id in countries_ids.split(',') if id])
        countries = countries.exists() if countries else False

        res.update(
            abidjans=abidjans,
            ivory_coast=ivory_coast,
            countries=countries,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrConfigParam = self.env['ir.config_parameter'].sudo()

        IrConfigParam.set_param('res.config.settings.abidjans', ','.join(map(str, self.abidjans.ids)))
        IrConfigParam.set_param('res.config.settings.ivory_coast', ','.join(map(str, self.ivory_coast.ids)))
        IrConfigParam.set_param('res.config.settings.countries', ','.join(map(str, self.countries.ids)))
