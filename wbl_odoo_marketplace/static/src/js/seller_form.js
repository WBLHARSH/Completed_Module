/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import VariantMixin from "@website_sale/js/variant_mixin";
import wSaleUtils from "@website_sale/js/website_sale_utils";
const cartHandlerMixin = wSaleUtils.cartHandlerMixin;
import { jsonrpc } from "@web/core/network/rpc_service";
import { registry } from '@web/core/registry';
import { renderToElement } from "@web/core/utils/render";
import { onWillStart } from "@odoo/owl";

publicWidget.registry.SellerShop = publicWidget.Widget.extend(VariantMixin, cartHandlerMixin, {
    selector: '#become_seller_form',
    events: {
        'change #shop_unique_url': '_onChangeShopUrl',
        'click #wbl_seller_form_submit': '_onClickSubmitSellerForm',
    },

    init() {
        this._super(...arguments);
        this.rpc = this.bindService("rpc");
    },

    async _onChangeShopUrl(ev) {
        let shop_url = $("#shop_unique_url").val();
        const specialCharPattern = /^[a-zA-Z0-9]+(?:[-_]?[a-zA-Z0-9]+)*$/;  // Regular expression to allow only alphanumeric and dashes/underscores in the middle

        // Check for special characters at the start or end of the URL
        if (!specialCharPattern.test(shop_url) || /[-_]$|^[-_]/.test(shop_url)) {
            this._showUrlInvalid("Special characters are not allowed at the beginning or end of the shop URL.");
            return;
        }

        const response = await this.rpc("/verify/shopUrl", { shop_url: shop_url });
        if (response) {
            this._showUrlInvalid("Sorry, this shop url is not available.");
        } else {
            this._showUrlValid();
        }
    },

    async _onClickSubmitSellerForm(ev) {
        ev.preventDefault();  // Prevent default form submission

        let shop_url = $("#shop_unique_url").val();
        const specialCharPattern = /^[a-zA-Z0-9]+(?:[-_]?[a-zA-Z0-9]+)*$/;

        // Validate URL format first
        if (!specialCharPattern.test(shop_url) || /[-_]$|^[-_]/.test(shop_url)) {
            this._showUrlInvalid("Special characters are not allowed at the beginning or end of the shop URL.");
            return;
        }

        // Check URL uniqueness
        const isUrlUnique = await this.rpc("/verify/shopUrl", { shop_url: shop_url });
        if (isUrlUnique) {
            this._showUrlInvalid("Sorry, this shop url is not available.");
        } else {
            this._showUrlValid();
            $("#become_seller_form").off('submit').submit();  // Allow form submission
        }
    },

    _showUrlInvalid(message) {
        $('#shop_unique_url').css('box-shadow', '0px 0px 10px red');
        $('#shop_url_error').text(message).show();
        $('#shop_url_error_icon').show();
        $('#shop_url_success_icon').hide();
    },

    _showUrlValid() {
        $('#shop_unique_url').css('box-shadow', '0px 0px 10px green');
        $('#shop_url_error').hide();
        $('#shop_url_success_icon').show();
        $('#shop_url_error_icon').hide();
    },
});
