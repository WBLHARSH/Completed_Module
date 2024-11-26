/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import wSaleUtils from "@website_sale/js/website_sale_utils";
import { OptionalProductsModal } from "@website_sale_product_configurator/js/sale_product_configurator_modal";
import "@website_sale/js/website_sale";
import { _t } from "@web/core/l10n/translation";
import { jsonrpc } from '@web/core/network/rpc_service';
import VariantMixin from '@website_sale/js/sale_variant_mixin';

//publicWidget.registry.NotifyButton = publicWidget.Widget.extend({
//    selector: '.oe_website_sale',
//    events: {
//        'click #wbl_notify': '_onButtonClick', // Use 'input' for real-time updates
//        'click #wbl_notify_form': '_onButtonNotifyClick',
//    },
//    start: function () {
//        this._super.apply(this, arguments);
//        this.rpc = this.bindService("rpc");
//    },
//    _onButtonClick(ev){
//       console.log("Hello Sweety");
//        $('#message_popup').modal("show");
//    },
//      async _onButtonNotifyClick(ev) {
//            ev.preventDefault(); // Prevent default form submission
//
//            console.log("Hello Harsh");
//
//            let nameElement = $("#wbl_name_notify");
//            let emailElement = $("#wbl_email_notify");
//            let productElement = $("#wbl_notify_product_id");
//            let MobileElement = $("#wbl_mobile_notify");
//            let commentElement = $("#wbl_comment_notify");
//            let nameRequired = $("#wbl_notify_required_name").val();
//            let emailRequired = $("#wbl_notify_required_email").val();
//            let phoneRequired = $("#wbl_notify_required_phone").val();
//            let commentRequired = $("#wbl_notify_required_comment").val();
//            console.log(nameRequired,emailRequired,phoneRequired,commentRequired)
//            alert("Working")
////            await this.rpc("/shop/preorder/notify", {
////                name: nameElement.val(),
////                email : emailElement.val(),
////                mobile:MobileElement.val(),
////                comment : commentElement.val(),
////                productId : productElement.val(),
////             }).then((response) => {
////                 if (response === true) {
////                 $('#message_popup').modal("hide");
////                 window.location.reload();
////        }
////         });
//
//        },
//});
//
//export default publicWidget.registry.NotifyButton;


publicWidget.registry.NotifyButton = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    events: {
        'click #wbl_notify': '_onButtonClick', // Use 'input' for real-time updates
        'click #wbl_notify_form': '_onButtonNotifyClick',
    },
    start: function () {
        this._super.apply(this, arguments);
        this.rpc = this.bindService("rpc");
},
    _onButtonClick(ev) {
        console.log("Hello Sweety");
        $('#message_popup').modal("show");
    },
    async _onButtonNotifyClick(ev) {
        ev.preventDefault(); // Prevent default form submission

        console.log("Hello Harsh");

        let nameElement = $("#wbl_name_notify");
        let emailElement = $("#wbl_email_notify");
        let productElement = $("#wbl_notify_product_id");
        let mobileElement = $("#wbl_mobile_notify");
        let commentElement = $("#wbl_comment_notify");
        let nameRequired = $("#wbl_notify_required_name").val() === "True";
        let emailRequired = $("#wbl_notify_required_email").val() === "True";
        let phoneRequired = $("#wbl_notify_required_phone").val() === "True";
        let commentRequired = $("#wbl_notify_required_comment").val() === "True";

        let hasErrors = false;

        if (nameRequired && !nameElement.val()) {
            nameElement.next('.error-message').text("Please fill the name field.");
            hasErrors = true;
        } else {
            nameElement.next('.error-message').text("");
        }

        if (emailRequired && !emailElement.val()) {
            emailElement.next('.error-message').text("Please fill the email field.");
            hasErrors = true;
        } else {
            emailElement.next('.error-message').text("");
        }

        if (phoneRequired && !mobileElement.val()) {
            mobileElement.next('.error-message').text("Please fill the mobile field.");
            hasErrors = true;
        } else {
            mobileElement.next('.error-message').text("");
        }

        if (commentRequired && !commentElement.val()) {
            commentElement.next('.error-message').text("Please fill the comment field.");
            hasErrors = true;
        } else {
            commentElement.next('.error-message').text("");
        }

        console.log(hasErrors, 'hasErrors');
        if (hasErrors) {
            return; // Do not proceed if there are errors
        }

        // Proceed with RPC call
        try {
            const response = await this.rpc("/shop/preorder/notify", {
                name: nameElement.val(),
                email: emailElement.val(),
                mobile: mobileElement.val(),
                comment: commentElement.val(),
                productId: productElement.val(),
            });
            if (response === true) {
                $('#message_popup').modal("hide");
                window.location.reload();
            }
        } catch (error) {
            console.error("Error during RPC call:", error);
        }
    },
});

export default publicWidget.registry.NotifyButton;