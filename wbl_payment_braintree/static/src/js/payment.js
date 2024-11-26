/** @odoo-module */

import publicWidget from "@web/legacy/js/public/public_widget";
import wSaleUtils from "@website_sale/js/website_sale_utils";
import { OptionalProductsModal } from "@website_sale_product_configurator/js/sale_product_configurator_modal";
import "@website_sale/js/website_sale";
import { _t } from "@web/core/l10n/translation";
import { jsonrpc } from '@web/core/network/rpc_service';
import VariantMixin from '@website_sale/js/sale_variant_mixin';
import { loadJS } from "@web/core/assets";


// Main code --------


publicWidget.registry.PaymentForm.include({

    /**
     * @override
     */
    init() {
        this._super(...arguments);
        this.rpc = this.bindService("rpc");
    },

    async _submitForm(ev) {
        const selectedPaymentMethod = this.$('input[name="o_payment_radio"]:checked').data('provider-code');
        if (selectedPaymentMethod !== 'braintree') {
            return await this._super(...arguments);
        }

        const dropinInstance = window.myDropinInstance; // Access the global instance
        if (dropinInstance) {
            // Make the callback function async
            dropinInstance.requestPaymentMethod(async (error, payload) => {
                if (error) {
                    console.error('Error getting payment method:', error);
                } else if (payload) {
                    const response = await this.rpc("/braintree/payment/process", {
                        paymentMethodNonce: payload.nonce,
                    });
                    if (response.result === 'success') {
                        ev.stopPropagation();
                        ev.preventDefault();

                        const checkedRadio = this.el.querySelector('input[name="o_payment_radio"]:checked');

                        // Block the entire UI to prevent fiddling with other widgets.
                        this._disableButton(true);

                        // Initiate the payment flow of the selected payment option.
                        const flow = this.paymentContext.flow = this._getPaymentFlow(checkedRadio);
                        const paymentOptionId = this.paymentContext.paymentOptionId = this._getPaymentOptionId(checkedRadio);

                        if (flow === 'token' && this.paymentContext['assignTokenRoute']) {
                            await this._assignToken(paymentOptionId);
                        } else {
                            const providerCode = this.paymentContext.providerCode = this._getProviderCode(checkedRadio);
                            const pmCode = this.paymentContext.paymentMethodCode = this._getPaymentMethodCode(checkedRadio);
                            this.paymentContext.providerId = this._getProviderId(checkedRadio);

                            if (this._getPaymentOptionType(checkedRadio) === 'token') {
                                this.paymentContext.tokenId = paymentOptionId;
                            } else {
                                this.paymentContext.paymentMethodId = paymentOptionId;
                            }

                            const inlineForm = this._getInlineForm(checkedRadio);
                            this.paymentContext.tokenizationRequested = inlineForm?.querySelector(
                                '[name="o_payment_tokenize_checkbox"]'
                            )?.checked ?? this.paymentContext['mode'] === 'validation';

                            await this._initiatePaymentFlow(providerCode, paymentOptionId, pmCode, flow);
                        }
                    }
                }
            });
        }
    },
});

export default publicWidget.registry.PaymentForm;

