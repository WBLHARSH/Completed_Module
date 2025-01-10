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

        let seller_name = $("#become_seller_name");
        let seller_phone = $("#become_seller_phone");
        let seller_email = $("#become_seller_email");
        let seller_country_id = $("#become_seller_country_id");
        let shop_name = $("#become_shop_name");
        let shop_url = $("#shop_unique_url");

        // Initialize validation flag
        let isValid = true;

        // Helper function to validate a field
        const validateField = (field, errorSpanId) => {
            const errorSpan = $(`#${errorSpanId}`);

            if (!field.val()) {
                field.css("border", "1px solid red");
                errorSpan.css("display", "inline"); // Show error message
                isValid = false;
            } else {
                field.css("border", "1px solid #ccc"); // Reset border
                errorSpan.css("display", "none"); // Hide error message
            }
        };

        // Validate all fields
        validateField(seller_name, "become-error-name");
        validateField(seller_phone, "become-error-phone");
        validateField(seller_email, "become-error-email");
        validateField(seller_country_id, "become-error-country");
        validateField(shop_name, "become-error-shop-name");
        validateField(shop_url, "become-error-shop-url");

        // If validation fails, stop further execution
        if (!isValid) {
            return;
        }

        // Check URL uniqueness
        const saveData = await this.rpc("/seller/form", { seller_name: seller_name.val(),seller_phone:seller_phone.val(),seller_email:seller_email.val(),seller_country_id:seller_country_id.val(),shop_name:shop_name.val(),shop_url:shop_url.val()});
        if (saveData.URL === '/web#action=wbl_odoo_marketplace.action_client_marketplace_menu') {
            window.location.href = saveData.URL;
        }
        if (saveData.URL === 'seller_exist'){
             $("#become_seller_exist_warning_id").css("display", "block");
        }
        if (saveData.URL === 'shop_url_exist'){
             $("#become_url_exist_warning_id").css("display", "block");
        }
    },

    _showUrlInvalid(message) {
        $("#become-error-shop-url").css("display", "none");
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