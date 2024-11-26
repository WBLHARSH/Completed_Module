/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { loadJS } from "@web/core/assets";
import paymentForm from '@payment/js/payment_form';
import paymentAirwallexMixin from '@wbl_payment_airwallex/js/payment_airwallex_mixin';

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
        if (providerCode !== 'airwallex') {
            this._super(...arguments);
            return;
        } else if (flow === 'token') {
            return;
        }
        this._setPaymentFlow('direct');
    },

    // #=== PAYMENT FLOW ===#

    async _processDirectFlow(providerCode, paymentOptionId, paymentMethodCode, processingValues) {
        if (providerCode !== 'airwallex') {
            this._super(...arguments);
            return;
        }
        paymentAirwallexMixin.processAirwallexPayment(processingValues);
    },
});