from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request
from datetime import datetime


class WebsiteSaleInherit(WebsiteSale):

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True, sitemap=False)
    def confirm_order(self, **post):
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order) or self.checkout_check_address(order)
        if redirection:
            return redirection
        order.order_line._compute_tax_id()
        request.session['sale_last_order_id'] = order.id
        request.website.sale_get_order(update_pricelist=False)
        extra_step = request.website.viewref('website_sale.extra_info')
        if extra_step.active:
            return request.redirect("/shop/extra_info")
        return request.redirect("/shop/payment")

    @http.route(['/shop/<model("product.template"):product>'], type='http', auth="public", website=True, sitemap=True)
    def product(self, product, category='', search='', **kwargs):
        print(product.preorder_when_qty_less_than_or_equal, 'qty_available')
        partner_id = request.env.user.partner_id.id if request.env.user else None
        product_tmpl_id = product.id
        total_booking_quantity = 0
        max_booking_quantity = 0
        current_date = datetime.now().date()
        if product.preorder_when_qty_less_than_or_equal and product.preorder_when_qty_less_than_or_equal >= product.qty_available:
            product.sudo().write({'can_be_preorder': True})
        if partner_id and partner_id != 4:
            sale_order_lines = request.env['sale.order.line'].search(
                [('product_id.product_tmpl_id', '=', product_tmpl_id)])
            total_booking_quantity = sum(line.product_uom_qty for line in sale_order_lines)

        if partner_id and partner_id != 4:
            sale_order_lines = request.env['sale.order.line'].search(
                [('product_id.product_tmpl_id', '=', product_tmpl_id),
                 ('order_partner_id', '=', partner_id)])
            max_booking_quantity = sum(line.product_uom_qty for line in sale_order_lines)

        notify_exists = request.env['notify.details'].search_count([
            ('product_id', '=', product_tmpl_id),
            ('partner_id', '=', partner_id),
        ]) > 0

        settings = request.env['res.config.settings'].sudo().get_values()

        can_be_preorder = product.can_be_preorder and (
                total_booking_quantity <= product.total_preorder_booking_qty) or (
                                  current_date == product.available_date)
        if not can_be_preorder:
            product.sudo().write({'can_be_preorder': False})

        response = super(WebsiteSaleInherit, self).product(product, category, search, **kwargs)
        response.qcontext.update({
            'can_be_preorder': can_be_preorder,
            'timer': product.available_date,
            'partner_id': partner_id,
            "enable_notify_me": settings.get("enable_notify_me"),
            "enable_notify_form": settings.get("enable_notify_form"),
            "notify_name": settings.get("enable_notify_name"),
            "notify_email": settings.get("enable_notify_email"),
            "notify_phone": settings.get("enable_notify_phone"),
            "notify_comment": settings.get("enable_notify_comment"),
            "is_name_required": settings.get("is_name_required"),
            "is_email_required": settings.get("is_email_required"),
            "is_phone_required": settings.get("is_phone_required"),
            "is_comment_required": settings.get("is_comment_required"),
            'preorder_policy_on_product': product.preorder_policy_on_product,
            'preorder_payment_type': product.preorder_payment_type,
            'preorder_button_text': settings.get("preorder_button_text"),
            'preorder_button_bc_color': settings.get("preorder_button_bc_color"),
            'preorder_button_text_color': settings.get("preorder_button_text_color"),
            'timer_text_color': settings.get("timer_text_color"),
            'timer_theme_color': settings.get("timer_theme_color"),
            'timer_on_product': settings.get("timer_on_product", False),
            'enable_preorder_label_on_product_page': settings.get("enable_preorder_label_on_product_page", False),
            'enable_preorder_label_on_shop_or_category_page': settings.get(
                "enable_preorder_label_on_shop_or_category_page", False),
            'preorder_label_text': settings.get("preorder_label_text"),
            'preorder_label_bc_color': settings.get("preorder_label_bc_color"),
            'preorder_label_text_color': settings.get("preorder_label_text_color"),
            'preorder_timer_design': settings.get("preorder_timer_design"),
            'total_booking_quantity': total_booking_quantity,
            'total_preorder_booking_qty': product.total_preorder_booking_qty,
            'max_booking_quantity': max_booking_quantity,  # add this to context
            'product_maximum_qty_per_customer': product.maximum_qty_per_customer,
            'notify_exists': notify_exists,  # add this to context
        })

        return response

    @http.route(['/shop', '/shop/page/<int:page>'], type='http', auth="public", website=True, sitemap=False)
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        response = super(WebsiteSaleInherit, self).shop(page, category, search, min_price, max_price, ppg, **post)

        if isinstance(response.qcontext, dict):
            # Fetch products with relevant fields only
            product_model = request.env['product.template']
            products = product_model.search([])
            settings = request.env['res.config.settings'].sudo().get_values()
            timer_theme_color = settings.get("timer_theme_color")
            timer_text_color = settings.get("timer_text_color")
            available_dates = {product.id: product.available_date.isoformat() if product.available_date else None
                               for product in products}
            can_be_preorder = {product.id: product.can_be_preorder
                               for product in products}

            response.qcontext.update({'available_dates': available_dates, 'can_be_preorder': can_be_preorder,
                                      'timer_text_color': timer_text_color, 'timer_theme_color': timer_theme_color,
                                      'timer_on_category': settings.get("timer_on_category", False),
                                      'enable_preorder_label_on_product_page': settings.get(
                                          "enable_preorder_label_on_product_page", False),
                                      'enable_preorder_label_on_shop_or_category_page': settings.get(
                                          "enable_preorder_label_on_shop_or_category_page", False),
                                      'preorder_label_text': settings.get("preorder_label_text"),
                                      'preorder_label_bc_color': settings.get("preorder_label_bc_color"),
                                      'preorder_label_text_color': settings.get("preorder_label_text_color"),
                                      'preorder_timer_design': settings.get("preorder_timer_design"),
                                      })
        return response

    @http.route(['/shop/cart'], type='http', auth="public", website=True, sitemap=False)
    def cart(self, access_token=None, revive='', **post):
        response = super(WebsiteSaleInherit, self).cart(access_token=access_token, revive=revive, **post)
        settings = request.env['res.config.settings'].sudo().get_values()

        product_model = request.env['product.product']  # Change this to 'product.product'
        products = product_model.search([])
        can_be_preorder = {product.id: product.can_be_preorder for product in products}

        response.qcontext.update({
            'enable_message_on_cart_page': settings.get("enable_message_on_cart_page"),
            'preorder_cart_page_message': settings.get("preorder_cart_page_message"),
            'preorder_cart_page_message_theme': settings.get("preorder_cart_page_message_theme"),
            'can_be_preorder': can_be_preorder,
        })
        return response

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(
            self, product_id, line_id=None, add_qty=None, set_qty=None, display=True, partial_statuses=None,
            dynamic_amount=None,
            product_custom_attribute_values=None, no_variant_attribute_values=None, **kw
    ):
        response = super(WebsiteSaleInherit, self).cart_update_json(product_id=product_id, line_id=line_id,
                                                                    add_qty=add_qty,
                                                                    set_qty=set_qty, display=display,
                                                                    product_custom_attribute_values=product_custom_attribute_values,
                                                                    no_variant_attribute_values=no_variant_attribute_values,
                                                                    partial_statuses=partial_statuses,
                                                                    dynamic_amount=dynamic_amount,
                                                                    kw=kw)
        print("testing cart update json")
        print("partial_statuses", partial_statuses, "dynamic_amount:", dynamic_amount)
        if partial_statuses or dynamic_amount:
            order = request.env['sale.order'].sudo().search([], limit=1)
            for rec in order:
                rec.write({'customised_products': partial_statuses})
                rec.write({'dynamic_amount': dynamic_amount})

        return response

    @http.route('/shop/payment/validate', type='http', auth="public", website=True, sitemap=False)
    def shop_payment_validate(self, sale_order_id=None, **post):
        response = super(WebsiteSaleInherit, self).shop_payment_validate(sale_order_id=sale_order_id, post=post)
        if sale_order_id is None:
            order = request.website.sale_get_order()
            if not order and 'sale_last_order_id' in request.session:
                last_order_id = request.session['sale_last_order_id']
                order = request.env['sale.order'].sudo().browse(last_order_id).exists()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')
        user = request.env['res.users'].browse(request.session.uid)

        second_payment_sale_order = request.env['sale.order.line'].sudo().search(
            [('state', '=', "sent"), ('post_payment', '=', True)], limit=1, order='id desc')

        for rec in second_payment_sale_order:
            partial_orders = request.env['product.preorder'].sudo().search([
                ('create_uid', '=', user.id),
                ('id', '=', rec.preorder_record)
            ])
            for partial_order in partial_orders:
                remaining_amount = 0
                final_paid_amount = float(partial_order.paid_amount) + float(partial_order.remaining_amount)
                partial_order.write({
                    'remaining_amount': remaining_amount,
                    'paid_amount': final_paid_amount,
                    'status': 'paid' if remaining_amount <= 0 else 'remaining'
                })

        # Add logic to update or create product_preorder records
        for line in order.order_line:
            if line.can_be_preorder:
                product = line.product_id
                list_price = product.lst_price or 0
                total_price_with_tax = list_price * line.product_uom_qty
                paid_amount = line.price_subtotal
                remaining_amount = total_price_with_tax - paid_amount

                preorder_record = request.env['product.preorder'].sudo().search([('sale_order_line_id', '=', line.id)],
                                                                                limit=1)
                if preorder_record:
                    preorder_record.write({
                        'paid_amount': paid_amount,
                        'total_amount': total_price_with_tax,
                        "remaining_amount": remaining_amount,
                        'payment_type': 'Partial Payment' if paid_amount < total_price_with_tax else 'Full Payment',
                        'status': 'remaining' if paid_amount < total_price_with_tax else 'paid',
                        'partner_id': order.partner_id.id,
                    })
                else:
                    request.env['product.preorder'].sudo().create({
                        'sale_order_line_id': line.id,
                        'payment_type': line.product_id.product_tmpl_id.preorder_payment_type,
                        'paid_amount': paid_amount,
                        'total_amount': total_price_with_tax,
                        "remaining_amount": remaining_amount,
                        'status': 'remaining' if paid_amount < total_price_with_tax else 'paid',
                        'partner_id': order.partner_id.id,
                    })

        return response
