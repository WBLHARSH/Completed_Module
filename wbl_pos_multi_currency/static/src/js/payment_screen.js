import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { onMounted,Component, useState } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { AlertDialog,ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { MultiCurrencyPopup } from "./multi_currency_popup";
import { _t } from "@web/core/l10n/translation";
var current_currency, currency_id;

patch(PaymentScreen.prototype, {
    setup() {
        super.setup();
        onMounted(this.enable_multi_currency.bind(this));
        current_currency = {
           rate: 1,
        };
        var currency = [];
        this.dialog = useService("dialog");
        if (this.pos.currency._raw.currency_params){
            currency.push(this.pos.currency._raw.currency_params);
        }
        this.multi_currency = useState({
            'currencies': currency
        });
    },

    _click_currency_popup() {
        try {
            const addPaymentLine = this.addMultiCurrencyPaymentLine.bind(this); // Bind the method
            this.dialog.add(MultiCurrencyPopup, { addPaymentLine });
        } catch (error) {
            console.log("An error occurred in _click_currency_popup:", error);
            return;
        }
    },

    // Add Payment Line
    async addMultiCurrencyPaymentLine() {
    try {
        var amount_val = document.getElementById('enter_amount').value;
        if (!amount_val || isNaN(amount_val)) {
            this.dialog.add(AlertDialog, {
                title: _t("Message Box"),
                body: _t("Please enter a valid amount."),
            });
            return;
        }

        const paymentMethod = this.pos.models["pos.payment.method"].get(1);
        if (this.pos.paymentTerminalInProgress && paymentMethod.use_payment_terminal) {
            this.dialog.add(AlertDialog, {
                title: _t("Error"),
                body: _t("There is already an electronic payment in progress."),
            });
            return;
        }

        const selectCurrencyElement = document.querySelector("#select_currency");
        const selectedOption = selectCurrencyElement.options[selectCurrencyElement.selectedIndex];
        const currency_id = selectedOption ? parseInt(selectedOption.value) : null;
        const current_currency = this.multi_currency.currencies[0].find(item => item.id === parseInt(currency_id));

        if (!current_currency) {
            console.error('Current currency not found');
            return;
        }

        // Original function: click_paymentmethods
        const result = this.currentOrder.add_paymentline(paymentMethod);
        if (!result) {
            throw new Error("Failed to add payment line.");
        }

        const update_amount = amount_val / current_currency.rate;
        await this.selectedPaymentLine.set_amount(update_amount);

        this.selectedPaymentLine.converted_currency = {
            'name': current_currency.display_name,
            'symbol': current_currency.symbol,
            'amount': amount_val,
        };
        this.selectedPaymentLine.payment_currency = current_currency.display_name;
        this.selectedPaymentLine.currency_amount = parseFloat(amount_val);
        this.selectedPaymentLine.payment_symbol = current_currency.symbol;

    } catch (error) {
        console.error("An error occurred while adding a multi-currency payment line:", error);
        this.dialog.add(AlertDialog, {
            title: _t("Error"),
            body: _t("An error occurred. Please try again or contact support."),
        });
    }
},


    // Hide The Multi Currency Button
    enable_multi_currency() {
        if (this.pos.config.enable_multi_currency == false) {
            document.getElementById('multi_currency_popup_button').style.display = 'none';
        }
    },

    // Update Payment Line
    updateSelectedPaymentline(amount = false) {
        var result = super.updateSelectedPaymentline(...arguments);
        if (this.pos.config.enable_multicurrency == true) {
            if (this.selectedPaymentLine) {
                var change_amount = this.selectedPaymentLine.amount * current_currency.rate;
                this.selectedPaymentLine.converted_currency = {
                    'name': current_currency.display_name,
                    'symbol': current_currency.symbol,
                    'amount': change_amount
                };
            }
        }
        return result;
    },
});
