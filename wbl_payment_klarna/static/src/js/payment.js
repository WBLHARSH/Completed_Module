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
        
        var checkoutContainer = document.getElementById('my-checkout-container')
		checkoutContainer.innerHTML = (document.getElementById("KCO").value).replace(/\\"/g, "\"").replace(/\\n/g, "");
		var scriptsTags = checkoutContainer.getElementsByTagName('script')
		for (var i = 0; i < scriptsTags.length; i++) {
			var parentNode = scriptsTags[i].parentNode
			var newScriptTag = document.createElement('script')
			newScriptTag.type = 'text/javascript'
			newScriptTag.text = scriptsTags[i].text
			parentNode.removeChild(scriptsTags[i])
			parentNode.appendChild(newScriptTag)
		}
		var response = await this._super(...arguments);
        return response;
       
    },
});

export default publicWidget.registry.PaymentForm;

