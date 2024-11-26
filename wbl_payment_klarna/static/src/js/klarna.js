/** @odoo-module */

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.HarshPayment = publicWidget.Widget.extend({
    selector: '#klarna_payment_div',

    start: function () {
        this._super.apply(this, arguments);
        this._initializeCheckout();
    },

    _initializeCheckout: function () {
        var checkoutContainer = document.getElementById('my-checkout-container');
        checkoutContainer.innerHTML = (document.getElementById("KCO").value).replace(/\\"/g, "\"").replace(/\\n/g, "");

        var scriptsTags = checkoutContainer.getElementsByTagName('script');
        for (var i = 0; i < scriptsTags.length; i++) {
            var parentNode = scriptsTags[i].parentNode;
            var newScriptTag = document.createElement('script');
            newScriptTag.type = 'text/javascript';
            newScriptTag.text = scriptsTags[i].text;
            parentNode.removeChild(scriptsTags[i]);
            parentNode.appendChild(newScriptTag);
        }
    },

    events: {
        'click #call_template_klarna': 'newCall',
    },

    newCall: async function(ev) {
        console.log("Hello Brother");
        this._initializeCheckout();
    }
});

export default publicWidget.registry.HarshPayment;
