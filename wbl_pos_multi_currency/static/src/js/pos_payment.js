import { PosPayment } from "@point_of_sale/app/models/pos_payment";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";

//Patching PosOrder
patch(PosPayment.prototype, {
    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        result.multiCurrencyAmount= this.currency_amount
        result.paymentCurrency= this.payment_currency
        result.paymentSymbol= this.payment_symbol
        return result;
    },
});