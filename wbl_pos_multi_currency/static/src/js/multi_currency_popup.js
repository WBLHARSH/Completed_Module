import { Dialog } from "@web/core/dialog/dialog";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useState } from "@odoo/owl";
import { Component } from "@odoo/owl";

export class MultiCurrencyPopup extends Component {
    static template = "wbl_pos_multi_currency.MultiCurrencyPopupNew";
    static components = { Dialog };
    static props = ["close", "addPaymentLine"];

    setup() {
        try {
            this.pos = usePos();
            this.state = useState({
                currentRate: "",
                enteredAmount: "",
                orderAmount: this.pos.get_order().get_total_with_tax() || 0,
                convertedOrderAmount: "",
            });

            const multiCurrencyIds = this.pos.currency._raw.currency_params || [];

            this.currencies = multiCurrencyIds.map(currency => ({
                code: currency.id,
                name: currency.name,
                rate: currency.rate,
            }));
        } catch (error) {
            console.error("Error during setup:", error);
        }
    }

    get currencyOptions() {
        try {
            return this.currencies.map(currency => ({
                value: currency.code,
                label: currency.name,
            }));
        } catch (error) {
            console.error("Error generating currency options:", error);
            return [];
        }
    }

    onCurrencyChange(event) {
        try {
            const selectedCurrencyCode = event.target.value;
            const selectedCurrency = this.currencies.find(
                currency => currency.code === parseInt(selectedCurrencyCode)
            );
            if (selectedCurrency) {
                this.state.currentRate = selectedCurrency.rate;
                this.calculateConvertedOrderAmount();
            } else {
                this.state.currentRate = "";
                this.state.convertedOrderAmount = "";
            }
        } catch (error) {
            console.error("Error during currency change:", error);
        }
    }

    calculateConvertedOrderAmount() {
        try {
            const rate = parseFloat(this.state.currentRate) || 0;
            const orderAmount = parseFloat(this.state.orderAmount) || 0;
            this.state.convertedOrderAmount = (rate * orderAmount).toFixed(2);
        } catch (error) {
            console.error("Error calculating converted order amount:", error);
            this.state.convertedOrderAmount = "";
        }
    }
}
