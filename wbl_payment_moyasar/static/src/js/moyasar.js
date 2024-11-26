/** @odoo-module */

import publicWidget from "@web/legacy/js/public/public_widget";
import { loadJS } from "@web/core/assets";

publicWidget.registry.HarshPayment = publicWidget.Widget.extend({
    selector: '#moyasar_payment_div',

    start: async function () {
        this._super.apply(this, arguments);
        await this._initializeCheckout();  // Await the initialization process
    },

    _initializeCheckout: async function () {
        // Load external JS scripts using the imported loadJS function
        this._loadMoyasarCSS();
        await loadJS('https://cdnjs.cloudflare.com/polyfill/v3/polyfill.min.js?version=4.8.0&features=fetch');
        await loadJS('https://cdn.moyasar.com/mpf/1.14.0/moyasar.js');
        const public_key = $('#moyasar_publishable_api_key').val();
        const moyasar_currency = $('#moyasar_currency').val();
        const moyasar_amount = $('#moyasar_amount').val();
        const moyasar_reference = $('#moyasar_reference').val();
        const callback_url = $('#callback_url').val();
        console.log('===='.public_key,moyasar_currency,moyasar_amount,moyasar_reference)
        // Initialize Moyasar
        Moyasar.init({
            element: '.mysr-form',
            amount: moyasar_amount,  // Amount in the smallest currency unit
            currency: moyasar_currency,
            description: moyasar_reference,
            publishable_api_key: public_key,
            callback_url: callback_url,
            methods: ['creditcard']
        });
    },

    _loadMoyasarCSS() {
        const linkElement = document.createElement('link');
        linkElement.rel = 'stylesheet';
        linkElement.href = 'https://cdn.moyasar.com/mpf/1.14.0/moyasar.css';
        document.head.appendChild(linkElement);
    },

});

export default publicWidget.registry.HarshPayment;
