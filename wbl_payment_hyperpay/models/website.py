# -*- coding: utf-8 -*-
#############################################################################
#
#    Copyright (C) 2024-TODAY
#    Author: Odoo DevSouls <odoodevsouls@gmailcom>
#
#############################################################################

import logging
from odoo import models, _, _lt

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    def _get_checkout_step_list(self):
        steps = super(Website, self)._get_checkout_step_list()
        steps[-1][0].append('wbl_payment_hyperpay.wbl_hyperpay_payment_form')
        return steps
