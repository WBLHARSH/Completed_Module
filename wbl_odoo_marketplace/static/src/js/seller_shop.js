/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import VariantMixin from "@website_sale/js/variant_mixin";
import wSaleUtils from "@website_sale/js/website_sale_utils";
const cartHandlerMixin = wSaleUtils.cartHandlerMixin;
import { jsonrpc } from "@web/core/network/rpc_service";
import { registry } from '@web/core/registry';
import { renderToElement } from "@web/core/utils/render";
import { onWillStart } from "@odoo/owl";


publicWidget.registry.ProductsListLayout = publicWidget.Widget.extend({
    selector: '.mp_shop_products_grid',
    events: {
        'click .wbl_add_to_cart': '_onClickAddToCartButton',
    },

    init() {
        this._super(...arguments);
        this.rpc = this.bindService("rpc");
    },

    _onClickAddToCartButton: async function (ev) {
        var $input = $(ev.currentTarget);
        var product_id = $input.attr('data-product-id');
        const data = await this.rpc("/shop/cart/update_json", {
            product_id: parseInt(product_id),
            add_qty: 1,
        });
        if (data.cart_quantity && (data.cart_quantity !== parseInt($(".my_cart_quantity").text()))) {
            wSaleUtils.updateCartNavBar(data);
        };
        return data;
    },
});
