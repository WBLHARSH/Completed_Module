from odoo import models, api
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError

class ResCurrency(models.Model):
    _inherit = 'res.currency'

    def _load_pos_data(self, data):
        domain = self._load_pos_data_domain(data)
        fields = self._load_pos_data_fields(data['pos.config']['data'][0]['id'])
        currency_ids =  data['pos.config']['data'][0]['currencies_ids']
        data = self.search_read(domain, fields, load=False, limit=1)
        data[0]['currency_params'] = self.env['res.currency'].search_read([('id', 'in', currency_ids)])
        return {
            'data': data,
            'fields': fields
        }

