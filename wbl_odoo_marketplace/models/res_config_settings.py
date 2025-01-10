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
from tokenize import String

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Product and Seller Approval
    seller_auto_approval = fields.Boolean(string='Seller Auto Approval')
    product_auto_approval = fields.Boolean(string='Product Auto Approval')
    commission = fields.Float(string="Commission")
    # -----------------------Mail & Notification----------------------------
    # Seller Mail & Notification
    seller_request_notify_to_admin = fields.Boolean(string='Enable Admin Notification')
    seller_request_notify_to_seller = fields.Boolean(string='Enable Seller Notification')
    seller_approved_notify_to_seller = fields.Boolean(string='Enable Seller Approved Notification')
    seller_denied_notify_to_admin = fields.Boolean(string='Enable Seller Denied Notification')
    # Seller Product Mail & Notification
    seller_request_for_product_approval = fields.Boolean(string='Enable Admin product Approval Notification')
    seller_product_approved_notify_to_seller = fields.Boolean(string='Enable Seller Product Approved Notification')
    seller_product_denied_notify_to_seller = fields.Boolean(string='Enable Seller Product Denied Notification')
    # Seller Payment Mail & Notification
    seller_request_for_payment = fields.Boolean(string='Enable Request For Payment Notification')
    admin_pay_to_seller = fields.Boolean(string='Enable Pay To Seller Notification')
    seller_payment_request_approved_notify_to_seller = fields.Boolean(
        string='Enable Seller Payment Request Approved Notification')
    seller_payment_request_denied_notify_to_seller = fields.Boolean(
        string='Enable Seller Payment Request Denied Notification')
    customer_query_notify_to_seller = fields.Boolean(string='Enable Seller Notification for Customer Queries')
    customer_query_notify_to_customer = fields.Boolean(string='Enable Notification for Customer When Query Sent to Seller')
    # Seller Page Heading
    banner_heading = fields.Text(string='Marketplace Banner Heading')
    # Promotion Number
    seller_community = fields.Char(string='Seller Community')
    online_business = fields.Char(string='Online Business')
    days_payment = fields.Char(string='Days Payment')
    pincodes_served = fields.Char(string='Pincodes Served')
    # Seller Love
    seller_love_short_description = fields.Text(string="Short Description")
    opportunity = fields.Text(string="Opportunity", help="Write in short description.")
    ease_of_doing_business = fields.Text(string="Ease of Doing Business", help="Write in short description.")
    growth = fields.Text(string="Growth", help="Write in short description.")
    additional_support = fields.Text(string="Additional Support", help="Write in short description.")
    # Marketplace Journey
    journey_short_description = fields.Text(string="Short Description")
    journey_create = fields.Text(string="Create", help="Write in short description.")
    journey_list = fields.Text(string="List", help="Write in short description.")
    journey_orders = fields.Text(string="Orders", help="Write in short description.")
    journey_shipment = fields.Text(string="Shipment", help="Write in short description.")
    journey_payment = fields.Text(string="Payment", help="Write in short description.")
    stock_location = fields.Many2one('stock.location', string='Stock Location')

    def set_values(self):
        response = super(ResConfigSettings, self).set_values()

        self.env['ir.config_parameter'].sudo().set_param(
            'default_stock_location', self.stock_location.id or False
        ),
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.seller_auto_approval',
                                                         self.seller_auto_approval)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.product_auto_approval',
                                                         self.product_auto_approval)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.commission', self.commission)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.seller_request_notify_to_admin',
                                                         self.seller_request_notify_to_admin)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.seller_request_notify_to_seller',
                                                         self.seller_request_notify_to_seller)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.seller_approved_notify_to_seller',
                                                         self.seller_approved_notify_to_seller)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.seller_denied_notify_to_admin',
                                                         self.seller_denied_notify_to_admin)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.seller_request_for_product_approval',
                                                         self.seller_request_for_product_approval)

        self.env['ir.config_parameter'].sudo().set_param(
            'wbl_odoo_marketplace.seller_product_approved_notify_to_seller',
            self.seller_product_approved_notify_to_seller)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.seller_product_denied_notify_to_seller',
                                                         self.seller_product_denied_notify_to_seller)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.seller_request_for_payment',
                                                         self.seller_request_for_payment)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.admin_pay_to_seller',
                                                         self.admin_pay_to_seller)
        self.env['ir.config_parameter'].sudo().set_param(
            'wbl_odoo_marketplace.seller_payment_request_approved_notify_to_seller',
            self.seller_payment_request_approved_notify_to_seller)
        self.env['ir.config_parameter'].sudo().set_param(
            'wbl_odoo_marketplace.seller_payment_request_denied_notify_to_seller',
            self.seller_payment_request_denied_notify_to_seller)
        self.env['ir.config_parameter'].sudo().set_param(
            'wbl_odoo_marketplace.customer_query_notify_to_seller',
            self.customer_query_notify_to_seller)
        self.env['ir.config_parameter'].sudo().set_param(
            'wbl_odoo_marketplace.customer_query_notify_to_customer',
            self.customer_query_notify_to_customer)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.banner_heading',
                                                         self.banner_heading)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.seller_community',
                                                         self.seller_community)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.online_business',
                                                         self.online_business)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.days_payment',
                                                         self.days_payment)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.pincodes_served',
                                                         self.pincodes_served)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.seller_love_short_description',
                                                         self.seller_love_short_description)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.opportunity',
                                                         self.opportunity)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.ease_of_doing_business',
                                                         self.ease_of_doing_business)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.growth',
                                                         self.growth)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.additional_support',
                                                         self.additional_support)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.journey_short_description',
                                                         self.journey_short_description)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.journey_create',
                                                         self.journey_create)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.journey_list',
                                                         self.journey_list)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.journey_orders',
                                                         self.journey_orders)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.journey_shipment',
                                                         self.journey_shipment)
        self.env['ir.config_parameter'].sudo().set_param('wbl_odoo_marketplace.journey_payment',
                                                         self.journey_payment)
        return response

    @api.model
    def get_values(self):
        response = super(ResConfigSettings, self).get_values()
        ir_config_parameter = self.env['ir.config_parameter'].sudo()
        stock_location_id = self.env['ir.config_parameter'].sudo().get_param('default_stock_location')
        response.update(
            seller_auto_approval=ir_config_parameter.get_param('wbl_odoo_marketplace.seller_auto_approval'),
            stock_location=int(stock_location_id) if stock_location_id else False,
            product_auto_approval=ir_config_parameter.get_param('wbl_odoo_marketplace.product_auto_approval'),
            commission=ir_config_parameter.get_param('wbl_odoo_marketplace.commission'),
            seller_request_notify_to_admin=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.seller_request_notify_to_admin'),
            seller_request_notify_to_seller=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.seller_request_notify_to_seller'),
            seller_approved_notify_to_seller=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.seller_approved_notify_to_seller'),
            seller_payment_request_denied_notify_to_seller=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.seller_payment_request_denied_notify_to_seller'),
            customer_query_notify_to_seller=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.customer_query_notify_to_seller'),
            customer_query_notify_to_customer=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.customer_query_notify_to_customer'),
            seller_request_for_product_approval=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.seller_request_for_product_approval'),
            seller_product_approved_notify_to_seller=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.seller_product_approved_notify_to_seller'),
            seller_product_denied_notify_to_seller=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.seller_product_denied_notify_to_seller'),
            seller_request_for_payment=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.seller_request_for_payment'),
            admin_pay_to_seller=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.admin_pay_to_seller'),
            seller_payment_request_approved_notify_to_seller=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.seller_payment_request_approved_notify_to_seller'),
            seller_denied_notify_to_admin=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.seller_denied_notify_to_admin'),
            banner_heading=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.banner_heading'),

            seller_community=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.seller_community'),
            online_business=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.online_business'),
            days_payment=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.days_payment'),
            pincodes_served=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.pincodes_served'),

            seller_love_short_description=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.seller_love_short_description'),
            opportunity=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.opportunity'),
            ease_of_doing_business=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.ease_of_doing_business'),
            growth=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.growth'),
            additional_support=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.additional_support'),

            journey_short_description=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.journey_short_description'),
            journey_create=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.journey_create'),
            journey_list=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.journey_list'),
            journey_orders=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.journey_orders'),
            journey_shipment=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.journey_shipment'),
            journey_payment=ir_config_parameter.get_param(
                'wbl_odoo_marketplace.journey_payment'),
        )
        return response
