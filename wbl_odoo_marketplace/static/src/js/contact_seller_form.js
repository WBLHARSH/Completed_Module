/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import VariantMixin from "@website_sale/js/variant_mixin";
import wSaleUtils from "@website_sale/js/website_sale_utils";
const cartHandlerMixin = wSaleUtils.cartHandlerMixin;
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.CustomerQueryForm = publicWidget.Widget.extend(VariantMixin, cartHandlerMixin, {
    selector: '#contact_seller_form',
    events: {
        'click #wbl_contact_seller_submit': '_onClickSubmitCustomerQueryForm',
    },

    init() {
        this._super(...arguments);
        this.rpc = this.bindService("rpc");
    },

    async _onClickSubmitCustomerQueryForm(ev) {
        // Prevent form submission
        ev.preventDefault();

        // Get field references
        const seller_id = $("#contact_seller_id");
        const seller_uid = $("#contact_seller_uid");
        const name = $("#contact_partner_name");
        const phone = $("#contact_partner_phone");
        const email = $("#contact_partner_email");
        const subject = $("#contact_subject");
        const question = $("#contact_question");

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
        validateField(name, "contact-error-name");
        validateField(phone, "contact-error-phone");
        validateField(email, "contact-error-email");
        validateField(subject, "contact-error-subject");
        validateField(question, "contact-error-question");

        // If validation fails, stop further execution
        if (!isValid) {
            return;
        }

        // Proceed with RPC call if all fields are valid
        const saveData = await this.rpc("/contact/seller", {
            seller_id: seller_id.val(),
            seller_uid: seller_uid.val(),
            name: name.val(),
            phone: phone.val(),
            email: email.val(),
            subject: subject.val(),
            question: question.val(),
        });

        if (saveData && saveData.URL && saveData.URL != 'exist') {
            // Redirect to the provided URL
            window.location.href = saveData.URL;
        } else {
            console.error("Invalid response or missing URL");
        }
        if (saveData.URL === 'exist'){
             $("#warning_for_customer_query").css("display", "block");
        }
    },
});