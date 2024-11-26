/** @odoo-module */


import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from '@web/core/network/rpc_service';
import { loadJS } from "@web/core/assets";

publicWidget.registry.HarshPayment = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    events: {
        'click input[name="o_payment_radio"]': 'onClickAddToCart',
    },

    start: function () {
        this._super.apply(this, arguments);
        this.rpc = this.bindService("rpc");
    },

    onClickAddToCart: async function(ev) {
        await loadJS('https://js.braintreegateway.com/web/dropin/1.43.0/js/dropin.min.js');
        const client_token = $('#wbl_client_token').val();

        braintree.dropin.create({
            authorization: client_token,
            container: '#dropin-container'
        }, (error, dropinInstance) => {
            if (error) {
                console.error('Error creating Drop-in instance:', error);
                const errorMessageElement = document.getElementById('error-message');
                errorMessageElement.textContent = 'Error Initializing Payment Form.';
                errorMessageElement.classList.add('alert', 'alert-warning');
                return;
            }
            // Assign the instance to a global object
            window.myDropinInstance = dropinInstance;
        });
    }
});

export default publicWidget.registry.HarshPayment;




