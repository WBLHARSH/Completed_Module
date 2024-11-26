/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { jsonrpc, RPCError } from "@web/core/network/rpc_service";
import { loadJS } from "@web/core/assets";

export default {

    /**
     * Simulate a feedback from a payment provider and redirect the customer to the status page.
     *
     * @private
     * @param {object} processingValues - The processing values of the transaction.
     * @return {void}
     */
    async processAirwallexPayment(processingValues) {
        const success_Url = $('#wbl_success_url').val();
        const cancel_Url = $('#wbl_fail_url').val();
        await loadJS('https://checkout.airwallex.com/assets/elements.bundle.min.js');
        const processingValuesQuery = new URLSearchParams(processingValues).toString();
        const successUrl = `${success_Url}?${processingValuesQuery}`;
        const cancelUrl = `${cancel_Url}?${processingValuesQuery}`;
        const response = await jsonrpc("/airwallex/payment/intent", {
            'paymentIntent': true,
        });

        if (response.intent_id && response.client_secret) {
            // Prevent default behavior that causes iframe reload
            event.preventDefault();

            Airwallex.redirectToCheckout({
                env: 'demo',
                mode: 'payment',
                intent_id: response.intent_id,
                client_secret: response.client_secret,
                currency: response.currency,
                successUrl: successUrl,
                failUrl: cancelUrl,
            });
        } else {
            console.error("Error in payment intent response:", response);
        }

    },

};
