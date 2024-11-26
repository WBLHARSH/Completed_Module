/** @odoo-module **/

// ###################################### Working #############################################
import publicWidget from "@web/legacy/js/public/public_widget";
import wSaleUtils from "@website_sale/js/website_sale_utils";
import { OptionalProductsModal } from "@website_sale_product_configurator/js/sale_product_configurator_modal";
import "@website_sale/js/website_sale";
import { _t } from "@web/core/l10n/translation";
import { jsonrpc } from '@web/core/network/rpc_service';
import VariantMixin from '@website_sale/js/sale_variant_mixin';

publicWidget.registry.WebsiteSale.include({
    _onChangeCombination: function (ev, $parent, combination) {
        var ret = this._super(...arguments);
        const quantityInput = this.$('input[name="add_qty"]');
        const deposit_amount = $('#wbl_deposit_price').val();
        const quantity = quantityInput.length ? parseInt(quantityInput.val()) : 1;
        var actual_price = combination.list_price;
        const balanceToPayAfter = (actual_price - (actual_price * deposit_amount / 100)) * quantity;
        const depositAmount = deposit_amount;
        const balanceToPayBefore = (actual_price * deposit_amount / 100) * quantity;
        const totalAmount = actual_price * quantity;

        $('#balance_to_pay_after').text(balanceToPayAfter.toFixed(2));
        $('#deposit_amount').text(depositAmount);
        $('#balance_to_pay_before').text(balanceToPayBefore.toFixed(2));
        $('#total_amount').text(totalAmount.toFixed(2));
        return ret;
    },
});
export default publicWidget.registry.WebsiteSalePartial;


// Call show Toast
publicWidget.registry.HarshPayment = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    events: {
        'click #Wbl_partial_box': '_onPartialCheckBoxClick',
        'click #wbl_full_payment': '_onFullPaymentCheckBoxClick',
        'click #add_to_cart_wrap': 'onClickAddToCart',
    },

    start: function () {
        this._super.apply(this, arguments);
        this.rpc = this.bindService("rpc");
        $('.toast').toast({
            autohide: false
        });
    },

    _onPartialCheckBoxClick: async function(ev) {
        $('.toast').toast('show');
    },

    _onFullPaymentCheckBoxClick: async function(ev){
        $('.toast').toast('hide');
    },
    onClickAddToCart: async function(ev){
        console.log("testing");
        const selected_payment_type = $('input[name="partial_radio_options"]:checked').val();
        const dynamic_price = $('#rangeValue').text();
        console.log("selected_payment_type" + selected_payment_type, 'Dynamic_price:', dynamic_price);
        if (selected_payment_type == "partial" || dynamic_price){
            console.log("test pass");
            const payment_type = selected_payment_type;
            console.log("test was" + payment_type);
            await this.rpc("/shop/cart/update_json", {
            partial_statuses: payment_type,
            dynamic_amount:dynamic_price,
            product_id :13,
            }).then((response) => {
                console.log(response);
            });
        }
        else{
            const payment_type = "full"
            await this.rpc("/shop/cart/update_json", {
            partial_statuses: payment_type,
            product_id :13,
            }).then((response) => {
                console.log(response);
            });
        }
    },
});

export default publicWidget.registry.HarshPayment;

// ###################################### Working #############################################

















