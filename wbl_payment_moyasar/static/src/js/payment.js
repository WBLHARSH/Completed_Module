/** @odoo-module **/
/* global Razorpay */

import { _t } from '@web/core/l10n/translation';
import { loadJS } from '@web/core/assets';
import paymentForm from '@payment/js/payment_form';

paymentForm.include({

    // #=== DOM MANIPULATION ===#

    /**
     * Update the payment context to set the flow to 'direct'.
     *
     * @override method from @payment/js/payment_form
     * @private
     * @param {number} providerId - The id of the selected payment option's provider.
     * @param {string} providerCode - The code of the selected payment option's provider.
     * @param {number} paymentOptionId - The id of the selected payment option
     * @param {string} paymentMethodCode - The code of the selected payment method, if any.
     * @param {string} flow - The online payment flow of the selected payment option.
     * @return {void}
     */
    async _prepareInlineForm(providerId, providerCode, paymentOptionId, paymentMethodCode, flow) {
        if (providerCode !== 'moyasar') {
            this._super(...arguments);
            return;
        }

        if (flow === 'token') {
            return; // No need to update the flow for tokens.
        }

        // Overwrite the flow of the select payment method.
        this._setPaymentFlow('direct');
    },

    // #=== PAYMENT FLOW ===#

    async _processDirectFlow(providerCode, paymentOptionId, paymentMethodCode, processingValues) {
    if (providerCode !== 'moyasar') {
        this._super(...arguments);
        return;
    }

    // Load necessary scripts
    this._loadMoyasarCSS();
    await loadJS('https://cdnjs.cloudflare.com/polyfill/v3/polyfill.min.js?version=4.8.0&features=fetch');
    await loadJS('https://cdn.moyasar.com/mpf/1.14.0/moyasar.js');

    // Initialize Moyasar
    Moyasar.init({
        element: '.mysr-form',
        amount: 1000,  // Amount in the smallest currency unit
        currency: 'SAR',
        description: 'Coffee Order #1',
        publishable_api_key: 'pk_test_Pjg8qkWHDgSmf84gw6FEwMqnqYfyC6ETYocykrNs',
        callback_url: 'http://triallll/payment.com',
        methods: ['creditcard']
    });

    // Ensure modal is shown after everything is loaded
    $('#message_popup').modal("show");
},
    _loadMoyasarCSS() {
        const linkElement = document.createElement('link');
        linkElement.rel = 'stylesheet';
        linkElement.href = 'https://cdn.moyasar.com/mpf/1.14.0/moyasar.css';
        document.head.appendChild(linkElement);
    },
});
