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

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import content_disposition, Controller, request, route
from odoo.http import request


class CustomerPortalInherit(CustomerPortal):
    MANDATORY_BILLING_FIELDS = ["name", "phone", "email", "street", "city", "country_id", "address", "selected_option"]
    OPTIONAL_BILLING_FIELDS = ["abidjan", "ivory_coast", "country", "zipcode", "state_id", "company_name", "vat"]

    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        res = super(CustomerPortalInherit, self).account(redirect=redirect, **post)
        # Fetch settings to update the context
        settings = request.env['res.config.settings'].sudo().get_values()
        res.qcontext.update({
            'abidjans': settings['abidjans'],
            'ivory_coast': settings['ivory_coast'],
            'country': settings['countries']
        })
        if post:
            partner = request.env.user.partner_id
            partner.sudo().write({
                'abidjan': int(post.get('abidjan')) if post.get('abidjan') else False,
                'ivory_coast': int(post.get('ivory_coast')) if post.get('ivory_coast') else False,
                'country': int(post.get('country')) if post.get('country') else False,
            })
        return res
