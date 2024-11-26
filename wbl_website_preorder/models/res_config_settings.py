from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    preorder_button_text = fields.Char(string="Preorder Button Text")
    preorder_button_bc_color = fields.Char(string="Preorder Button Background Color")
    preorder_button_text_color = fields.Char(string="Preorder Button Text Color")
    timer_on_product = fields.Boolean(string="Timer On Product")
    timer_on_category = fields.Boolean(string="Timer On Category")
    timer_theme_color = fields.Char(string="Timer Theme Color")
    timer_text_color = fields.Char(string="Timer Text Color")
    minimum_purchase_qty = fields.Integer(string="Minimum Purchase Quantity")
    maximum_purchase_qty = fields.Integer(string="Maximum Purchase Quantity")
    total_preorder_booking_qty = fields.Integer(string="Total Preorder Booking Quantity")
    available_date = fields.Date(string="Available Date")
    preorder_payment_type = fields.Selection(
        selection=[('Full payment', 'full payment'), ('Partial payment', 'partial payment'),
                   ('Dynamic payment', 'dynamic payment')], string="Preorder Payment Type")
    deposit_amount = fields.Float(string='Deposit Amount')
    preorder_when_qty_less_than_or_equal = fields.Integer(string="Allow Preorder When Quantity Less Than Or Equal")
    preorder_policy_on_product = fields.Html(string="Preorder Policy On Product")
    enable_preorder_label_on_product_page = fields.Boolean(string="Enable Preorder Label On Product Page")
    enable_preorder_label_on_shop_or_category_page = fields.Boolean(
        string="Enable Preorder Label On Shop Or Category Page")
    preorder_label_text = fields.Char(string="Preorder Label Text")
    preorder_label_bc_color = fields.Char(string="Preorder Label Background Color")
    preorder_label_text_color = fields.Char(string="Preorder Label Text Color")
    preorder_timer_design = fields.Selection(
        selection=[('circle timer', 'Circle Timer'), ('square timer', 'Square Timer'), ],
        string="Preorder Timer Design", default='circle timer')
    enable_message_on_cart_page = fields.Boolean(string="Enable To Display Message Under Product On Cart Page")
    preorder_cart_page_message = fields.Text(string="Preorder Cart Page Message")
    preorder_cart_page_message_theme = fields.Selection(
        selection=[('alert-primary', 'Alert Primary'), ('alert-secondary', 'Alert Secondary'),
                   ('alert-success', 'Alert Success'), ('alert-danger', 'Alert Danger'),
                   ('alert-warning', 'Alert Warning'), ('alert-info', "Alert Info"), ('alert-light', 'Alert Light'),
                   ('alert-dark', 'Alert Dark')])
    # Notify Fields
    enable_notify_me = fields.Boolean(string="Enable Notify Me")
    enable_notify_form = fields.Boolean(string="Enable Notify Form")
    enable_notify_name = fields.Boolean(string="Enable Notify Name")
    enable_notify_email = fields.Boolean(string="Enable Notify Email")
    enable_notify_phone = fields.Boolean(string="Enable Notify Phone")
    enable_notify_comment = fields.Boolean(string="Enable Notify Comment")
    is_name_required = fields.Boolean(string="Is Name Required")
    is_email_required = fields.Boolean(string="Is Email Required")
    is_phone_required = fields.Boolean(string="Is Phone Required")
    is_comment_required = fields.Boolean(string="Is Comment Required")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrConfigParam = self.env['ir.config_parameter'].sudo()

        res.update(
            preorder_button_text=IrConfigParam.get_param('res.config.settings.preorder_button_text', default=''),
            preorder_button_bc_color=IrConfigParam.get_param('res.config.settings.preorder_button_bc_color',
                                                             default=''),
            preorder_button_text_color=IrConfigParam.get_param('res.config.settings.preorder_button_text_color',
                                                               default=''),
            timer_on_product=IrConfigParam.get_param('res.config.settings.timer_on_product', default=False),
            timer_on_category=IrConfigParam.get_param('res.config.settings.timer_on_category', default=False),
            timer_theme_color=IrConfigParam.get_param('res.config.settings.timer_theme_color', default=''),
            timer_text_color=IrConfigParam.get_param('res.config.settings.timer_text_color', default=''),
            minimum_purchase_qty=int(IrConfigParam.get_param('res.config.settings.minimum_purchase_qty', default=0)),
            maximum_purchase_qty=int(IrConfigParam.get_param('res.config.settings.maximum_purchase_qty', default=0)),
            total_preorder_booking_qty=int(
                IrConfigParam.get_param('res.config.settings.total_preorder_booking_qty', default=0)),
            available_date=IrConfigParam.get_param('res.config.settings.available_date', default=False),
            preorder_payment_type=IrConfigParam.get_param('res.config.settings.preorder_payment_type',
                                                          default='Full payment'),
            deposit_amount=float(IrConfigParam.get_param('res.config.settings.deposit_amount', default=0.0)),
            preorder_when_qty_less_than_or_equal=int(
                IrConfigParam.get_param('res.config.settings.preorder_when_qty_less_than_or_equal', default=0)),
            preorder_policy_on_product=IrConfigParam.get_param('res.config.settings.preorder_policy_on_product',
                                                               default=''),
            enable_preorder_label_on_product_page=IrConfigParam.get_param(
                'res.config.settings.enable_preorder_label_on_product_page', default=False),
            enable_preorder_label_on_shop_or_category_page=IrConfigParam.get_param(
                'res.config.settings.enable_preorder_label_on_shop_or_category_page', default=False),
            preorder_label_text=IrConfigParam.get_param('res.config.settings.preorder_label_text', default=''),
            preorder_label_bc_color=IrConfigParam.get_param('res.config.settings.preorder_label_bc_color',
                                                            default=''),
            preorder_label_text_color=IrConfigParam.get_param('res.config.settings.preorder_label_text_color',
                                                              default=''),
            preorder_timer_design=IrConfigParam.get_param('res.config.settings.preorder_timer_design',
                                                          default='circle timer'),
            enable_message_on_cart_page=IrConfigParam.get_param('res.config.settings.enable_message_on_cart_page',
                                                                default=False),
            preorder_cart_page_message=IrConfigParam.get_param('res.config.settings.preorder_cart_page_message',
                                                               default=''),
            preorder_cart_page_message_theme=IrConfigParam.get_param(
                'res.config.settings.preorder_cart_page_message_theme',
                default='alert-info'),

            enable_notify_me=IrConfigParam.get_param('res.config.settings.enable_notify_me', default=False),
            enable_notify_form=IrConfigParam.get_param('res.config.settings.enable_notify_form', default=False),

            enable_notify_name=IrConfigParam.get_param('res.config.settings.enable_notify_name', default=False),
            enable_notify_email=IrConfigParam.get_param('res.config.settings.enable_notify_email', default=False),
            enable_notify_phone=IrConfigParam.get_param('res.config.settings.enable_notify_phone', default=False),
            enable_notify_comment=IrConfigParam.get_param('res.config.settings.enable_notify_comment', default=False),

            is_name_required=IrConfigParam.get_param('res.config.settings.is_name_required', default=False),
            is_email_required=IrConfigParam.get_param('res.config.settings.is_email_required', default=False),
            is_phone_required=IrConfigParam.get_param('res.config.settings.is_phone_required', default=False),
            is_comment_required=IrConfigParam.get_param('res.config.settings.is_comment_required', default=False),
        )

        return res

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrConfigParam = self.env['ir.config_parameter'].sudo()

        IrConfigParam.set_param('res.config.settings.preorder_button_text', self.preorder_button_text)
        IrConfigParam.set_param('res.config.settings.preorder_button_bc_color', self.preorder_button_bc_color)
        IrConfigParam.set_param('res.config.settings.preorder_button_text_color', self.preorder_button_text_color)
        IrConfigParam.set_param('res.config.settings.timer_on_product', self.timer_on_product)
        IrConfigParam.set_param('res.config.settings.timer_on_category', self.timer_on_category)
        IrConfigParam.set_param('res.config.settings.timer_theme_color', self.timer_theme_color)
        IrConfigParam.set_param('res.config.settings.timer_text_color', self.timer_text_color)
        IrConfigParam.set_param('res.config.settings.minimum_purchase_qty', self.minimum_purchase_qty)
        IrConfigParam.set_param('res.config.settings.maximum_purchase_qty', self.maximum_purchase_qty)
        IrConfigParam.set_param('res.config.settings.total_preorder_booking_qty', self.total_preorder_booking_qty)
        IrConfigParam.set_param('res.config.settings.available_date', self.available_date)
        IrConfigParam.set_param('res.config.settings.preorder_payment_type', self.preorder_payment_type)
        IrConfigParam.set_param('res.config.settings.deposit_amount', self.deposit_amount)
        IrConfigParam.set_param('res.config.settings.preorder_when_qty_less_than_or_equal',
                                self.preorder_when_qty_less_than_or_equal)
        IrConfigParam.set_param('res.config.settings.preorder_policy_on_product', self.preorder_policy_on_product)
        IrConfigParam.set_param('res.config.settings.enable_preorder_label_on_product_page',
                                self.enable_preorder_label_on_product_page)
        IrConfigParam.set_param('res.config.settings.enable_preorder_label_on_shop_or_category_page',
                                self.enable_preorder_label_on_shop_or_category_page)
        IrConfigParam.set_param('res.config.settings.preorder_label_text', self.preorder_label_text)
        IrConfigParam.set_param('res.config.settings.preorder_label_bc_color', self.preorder_label_bc_color)
        IrConfigParam.set_param('res.config.settings.preorder_label_text_color', self.preorder_label_text_color)
        IrConfigParam.set_param('res.config.settings.preorder_timer_design', self.preorder_timer_design)
        IrConfigParam.set_param('res.config.settings.enable_message_on_cart_page', self.enable_message_on_cart_page)
        IrConfigParam.set_param('res.config.settings.preorder_cart_page_message', self.preorder_cart_page_message)
        IrConfigParam.set_param('res.config.settings.preorder_cart_page_message_theme',
                                self.preorder_cart_page_message_theme)

        IrConfigParam.set_param('res.config.settings.enable_notify_me', self.enable_notify_me)
        IrConfigParam.set_param('res.config.settings.enable_notify_form', self.enable_notify_form)
        IrConfigParam.set_param('res.config.settings.enable_notify_name', self.enable_notify_name)
        IrConfigParam.set_param('res.config.settings.enable_notify_email', self.enable_notify_email)
        IrConfigParam.set_param('res.config.settings.enable_notify_phone', self.enable_notify_phone)
        IrConfigParam.set_param('res.config.settings.enable_notify_comment', self.enable_notify_comment)
        IrConfigParam.set_param('res.config.settings.is_name_required', self.is_name_required)
        IrConfigParam.set_param('res.config.settings.is_email_required', self.is_email_required)
        IrConfigParam.set_param('res.config.settings.is_phone_required', self.is_phone_required)
        IrConfigParam.set_param('res.config.settings.is_comment_required', self.is_comment_required)

    @api.onchange('enable_notify_name')
    def _onchange_enable_notify_name(self):
        if not self.enable_notify_name:
            self.is_name_required = False

    @api.onchange('enable_notify_email')
    def _onchange_enable_notify_email(self):
        if not self.enable_notify_email:
            self.is_email_required = False

    @api.onchange('enable_notify_phone')
    def _onchange_enable_notify_phone(self):
        if not self.enable_notify_phone:
            self.is_phone_required = False

    @api.onchange('enable_notify_comment')
    def _onchange_enable_notify_comment(self):
        if not self.enable_notify_comment:
            self.is_comment_required = False
