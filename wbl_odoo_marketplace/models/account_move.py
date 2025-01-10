from odoo import fields, models, api, _
from collections import defaultdict
from odoo.http import request


class AccountMove(models.Model):
    _inherit = 'account.move'

    seller_id = fields.Many2one(comodel_name='marketplace.seller', string='Seller')
    user_id = fields.Many2one(comodel_name='res.users')

    @api.depends('amount_residual', 'move_type', 'state', 'company_id')
    def _compute_payment_state(self):
        stored_ids = tuple(self.ids)
        if stored_ids:
            self.env['account.partial.reconcile'].flush_model()
            self.env['account.payment'].flush_model(['is_matched'])

            queries = []
            for source_field, counterpart_field in (('debit', 'credit'), ('credit', 'debit')):
                queries.append(f'''
                        SELECT
                            source_line.id AS source_line_id,
                            source_line.move_id AS source_move_id,
                            account.account_type AS source_line_account_type,
                            ARRAY_AGG(counterpart_move.move_type) AS counterpart_move_types,
                            COALESCE(BOOL_AND(COALESCE(pay.is_matched, FALSE))
                                FILTER (WHERE counterpart_move.payment_id IS NOT NULL), TRUE) AS all_payments_matched,
                            BOOL_OR(COALESCE(BOOL(pay.id), FALSE)) as has_payment,
                            BOOL_OR(COALESCE(BOOL(counterpart_move.statement_line_id), FALSE)) as has_st_line
                        FROM account_partial_reconcile part
                        JOIN account_move_line source_line ON source_line.id = part.{source_field}_move_id
                        JOIN account_account account ON account.id = source_line.account_id
                        JOIN account_move_line counterpart_line ON counterpart_line.id = part.{counterpart_field}_move_id
                        JOIN account_move counterpart_move ON counterpart_move.id = counterpart_line.move_id
                        LEFT JOIN account_payment pay ON pay.id = counterpart_move.payment_id
                        WHERE source_line.move_id IN %s AND counterpart_line.move_id != source_line.move_id
                        GROUP BY source_line.id, source_line.move_id, account.account_type
                    ''')

            self._cr.execute(' UNION ALL '.join(queries), [stored_ids, stored_ids])

            payment_data = defaultdict(lambda: [])
            for row in self._cr.dictfetchall():
                payment_data[row['source_move_id']].append(row)
        else:
            payment_data = {}

        for invoice in self:
            if invoice.payment_state == 'invoicing_legacy':
                continue

            currencies = invoice._get_lines_onchange_currency().currency_id
            currency = currencies if len(currencies) == 1 else invoice.company_id.currency_id
            reconciliation_vals = payment_data.get(invoice.id, [])
            payment_state_matters = invoice.is_invoice(True)

            if payment_state_matters:
                reconciliation_vals = [x for x in reconciliation_vals if
                                       x['source_line_account_type'] in ('asset_receivable', 'liability_payable')]

            new_pmt_state = 'not_paid'
            if invoice.state == 'posted':
                if payment_state_matters:
                    if currency.is_zero(invoice.amount_residual):
                        if any(x['has_payment'] or x['has_st_line'] for x in reconciliation_vals):
                            if all(x['all_payments_matched'] for x in reconciliation_vals):
                                new_pmt_state = 'paid'
                            else:
                                new_pmt_state = invoice._get_invoice_in_payment_state()
                        else:
                            new_pmt_state = 'paid'

                            reverse_move_types = set()
                            for x in reconciliation_vals:
                                for move_type in x['counterpart_move_types']:
                                    reverse_move_types.add(move_type)

                            in_reverse = (invoice.move_type in ('in_invoice', 'in_receipt')
                                          and (reverse_move_types == {'in_refund'} or reverse_move_types == {
                                        'in_refund', 'entry'}))
                            out_reverse = (invoice.move_type in ('out_invoice', 'out_receipt')
                                           and (reverse_move_types == {'out_refund'} or reverse_move_types == {
                                        'out_refund', 'entry'}))
                            misc_reverse = (invoice.move_type in ('entry', 'out_refund', 'in_refund')
                                            and reverse_move_types == {'entry'})
                            if in_reverse or out_reverse or misc_reverse:
                                new_pmt_state = 'reversed'

                    elif reconciliation_vals:
                        new_pmt_state = 'partial'

                    # Generate a credit entry for each product if the state changes to 'paid'
            if new_pmt_state == 'paid' and invoice.payment_state != 'paid':
                for line in invoice.invoice_line_ids:
                    product = line.product_id
                    price_total = line.price_total
                    seller_id = self.invoice_seller_id(product)
                    seller_amount = self._calculate_seller_amount(price_total)
                    if seller_id:
                        self.env['marketplace.seller.payment'].create({
                            'seller_payment_reference': self.env['ir.sequence'].next_by_code(
                                'marketplace.seller.payment.credit') or '/',
                            'seller_id': seller_id.id,
                            'user_id': seller_id.user_id.id,
                            'payment_amount': seller_amount,
                            'payment_description': _('Credit entry for product %s in invoice %s') % (
                                product.display_name, invoice.name),
                            'payment_type': 'credit',
                            'state': 'approved'
                        })

            invoice.payment_state = new_pmt_state

    def invoice_seller_id(self, product_id):
        mp_product_id = self.env['mp.seller.product'].sudo().search([('product_id', '=', product_id.id)])
        seller_id = mp_product_id.seller_id
        return seller_id

    def _calculate_seller_amount(self, price_total):
        if price_total:
            config_param = request.env['res.config.settings'].sudo().get_values()
            commission = config_param['commission']
            admin_commission = float(price_total) * float(commission)
            seller_amount = price_total - admin_commission
            return seller_amount
