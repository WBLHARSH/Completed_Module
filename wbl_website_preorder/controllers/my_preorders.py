from odoo import http
from odoo.http import request


class MyPortalPreorderController(http.Controller):
    @http.route('/my/preorders', website=True, auth='public')
    def portal_preorder(self, **kw):
        current_partner_id = request.env.user.partner_id.id
        sale_order_lines = request.env['sale.order.line'].search([
            ('order_partner_id', '=', current_partner_id),
            ('product_id.can_be_preorder', '=', True)
        ])
        preorder_details = []

        for sale_order_line in sale_order_lines:
            preorders = request.env['product.preorder'].search([
                ('sale_order_line_id', '=', sale_order_line.id)
            ])
            for preorder in preorders:
                remaining_amount = preorder.remaining_amount
                total_amount = preorder.total_amount
                view_order = 'orders/' + str(preorder.sale_order_id.id)
                preorder_details.append({
                    'sale_order_line': sale_order_line,
                    'preorder': preorder,
                    'remaining_amount': float(remaining_amount),
                    'total_amount': total_amount,
                    'view_order': view_order
                })
        count_preorder = len(preorder_details)
        installment_fees = request.env['product.product'].sudo().search([('default_code', '=', 'PayInstallment_012')])
        values = {
            'preorder_details': preorder_details,
            'count_preorder': count_preorder,
            'installment_fees': installment_fees,
        }
        return request.render('wbl_website_preorder.wbl_my_portal_preorder_view', values)

    @http.route('/shop/notify', website=True, type='http', auth='public')
    def preorder_notification(self, **kw):
        partner_id = request.env.user.partner_id.id if request.env.user else None
        product_id = kw.get('product_id')

        # Check if the record already exists
        existing_record = request.env['notify.details'].sudo().search_count([
            ('partner_id', '=', partner_id),
            ('product_id', '=', product_id)
        ])

        if existing_record == 0:
            # Create a new record only if no existing record is found
            request.env['notify.details'].sudo().create({
                'partner_id': partner_id,
                'product_id': product_id,
                'Name': request.env.user.partner_id.name if partner_id else '',
                'email': request.env.user.partner_id.email if partner_id else '',
                'phone': request.env.user.partner_id.phone if partner_id else '',
                'comment': ''  # This could be populated based on other logic or remain empty
            })

        return request.redirect(f'/shop/{product_id}')

    @http.route('/shop/preorder/notify', type='json', auth='public', website=True)
    def preorder_not(self, name=None, email=None, mobile=None, comment=None, productId=None, **kw):
        partner_id = request.env.user.partner_id.id if request.env.user else None
        print(mobile, name, email, productId, partner_id, "hello")
        if productId:
            existing_record = request.env['notify.details'].sudo().search_count([
                ('partner_id', '=', partner_id),
                ('product_id', '=', productId)
            ])

            if existing_record == 0:
                request.env['notify.details'].sudo().create({
                    'partner_id': partner_id,
                    'product_id': productId,
                    'Name': name,
                    'email': email,
                    'phone': mobile,
                    'comment': comment
                })
            return True


