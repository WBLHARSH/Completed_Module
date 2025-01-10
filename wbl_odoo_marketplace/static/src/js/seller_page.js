/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import VariantMixin from "@website_sale/js/variant_mixin";
import wSaleUtils from "@website_sale/js/website_sale_utils";
const cartHandlerMixin = wSaleUtils.cartHandlerMixin;
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.SellerQueryForm = publicWidget.Widget.extend(VariantMixin, cartHandlerMixin, {
    selector: '#seller_query_form_id',
    events: {
        'click #seller_query_submit_button': '_onClickSubmitSellerQueryForm',
    },

    init() {
        this._super(...arguments);
        this.rpc = this.bindService("rpc");
    },

    async _onClickSubmitSellerQueryForm(ev) {
        // Prevent form submission
        ev.preventDefault();

        // Get field references
        const name = $("#seller_query_name");
        const email = $("#seller_query_email");
        const topic = $("#seller_query_topic");
        const message = $("#seller_query_message");

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
        validateField(name, "error-name");
        validateField(email, "error-email");
        validateField(topic, "error-topic");
        validateField(message, "error-message");

        // If validation fails, stop further execution
        if (!isValid) {
            return;
        }

        // Proceed with RPC call if all fields are valid
        const saveData = await this.rpc("/seller/query", {
            name: name.val(),
            email: email.val(),
            topic: topic.val(),
            message: message.val(),
        });

        if (saveData && saveData.URL && saveData.URL != 'exist') {
            // Redirect to the provided URL
            window.location.href = saveData.URL;
        } else {
            console.error("Invalid response or missing URL");
        }
        if (saveData.URL === 'exist'){
             $("#seller_query_warning_id").css("display", "block");
        }
    },
});