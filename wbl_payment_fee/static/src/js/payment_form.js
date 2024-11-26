/** @odoo-module **/

import { Component } from '@odoo/owl';
import publicWidget from '@web/legacy/js/public/public_widget';
import { browser } from '@web/core/browser/browser';
import { _t } from '@web/core/l10n/translation';
import { RPCError } from '@web/core/network/rpc_service';

export const websiteCashOnDelivery = publicWidget.Widget.extend({
    selector: '#o_payment_form',
    events: Object.assign({}, publicWidget.Widget.prototype.events, {
        'click [name="o_payment_radio"]': '_selectPaymentOption',
    }),

    /**
     * @override
     */
    init() {
        this._super(...arguments);
        this.rpc = this.bindService("rpc");
        this.orm = this.bindService("orm");
    },
    _selectPaymentOption: async function (ev) {
        const checkedRadio = ev.target;
        var providerId = Number(checkedRadio.dataset['providerId']);
        var providerCode = checkedRadio.dataset['providerCode'];
        const result = await this.rpc('/provider/detail', {
            'provider_id': providerId,
        });
        this.result = result;
        var amountTax = document.querySelector('#order_total_taxes .monetary_field');
        var SubTotalAmount = document.querySelector('#order_total_untaxed .monetary_field');
        var paymentFee = document.querySelector('#wbl_payment_fee');
        var amountTotal = document.querySelectorAll('#order_total .monetary_field, #amount_total_summary.monetary_field');

        if (result.is_payment_fee) {
            amountTax.innerHTML = result.new_amount_tax;
            SubTotalAmount.innerHTML = result.new_subtotal_amount;
            paymentFee.innerHTML = result.payment_fee;
            amountTotal.forEach(total => total.innerHTML = result.new_amount_total);
            $("#cod_payment_fee").show();
        } else {
            SubTotalAmount.innerHTML = result.new_subtotal_amount;
            amountTax.innerHTML = result.new_amount_tax;
            amountTotal.forEach(total => total.innerHTML = result.new_amount_total);
            $("#cod_payment_fee").hide();
        }
    }
});
publicWidget.registry.websiteCashOnDelivery =  websiteCashOnDelivery;
