/* @odoo-module */

import publicWidget from "@web/legacy/js/public/public_widget";
import wSaleUtils from "@website_sale/js/website_sale_utils";
import { OptionalProductsModal } from "@website_sale_product_configurator/js/sale_product_configurator_modal";
import "@website_sale/js/website_sale";
import { _t } from "@web/core/l10n/translation";
import { jsonrpc } from '@web/core/network/rpc_service';
import VariantMixin from '@website_sale/js/sale_variant_mixin';

publicWidget.registry.PaymentForm.include({
    async _submitForm(ev) {
        var desire = $('#wbl_desire_date').val();
        var minimum_desire = parseInt($('#minimum_desire').val());
        var maximum_desire = parseInt($('#maximum_desire').val());

        var today1 = new Date();
        var today2 = new Date();
        var min_date = new Date(today1.setDate(today1.getDate() + minimum_desire));
        var max_date = new Date(today2.setDate(today2.getDate() + maximum_desire));
        var desireDate = desire ? new Date(desire) : null;
        var pop_message_text = `You can select date greater than ${minimum_desire} day and lower than ${maximum_desire} day.`
        if (desireDate < min_date || desireDate > max_date) {
            $('#message_popup').modal("show");
            $('#popup_message_text').text(pop_message_text);
            return false;
        }
        var response = await this._super(...arguments);
        return response;
    },
});

export default publicWidget.registry.PaymentFormDesireDate;
