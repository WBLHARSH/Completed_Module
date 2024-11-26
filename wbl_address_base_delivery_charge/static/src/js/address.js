/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import "@website_sale/js/website_sale";
import { _t } from "@web/core/l10n/translation";

publicWidget.registry.AddressHide = publicWidget.Widget.extend({
    selector: '.checkout_autoformat',
    events: {
        'click .form-check-input': '_onButtonShowAddress',
    },
    start: function () {
        this._super.apply(this, arguments);
        this.rpc = this.bindService("rpc");
    },
    // Show and Hide Dropdown on Radio Button Click
    async _onButtonShowAddress(ev) {
        const selectedAddressId = this.$('input[name="selected_option"]:checked').attr('id');
        const addresses = {
            address_abidjan: document.getElementById("wbl_abidjan"),
            address_ivory_coast: document.getElementById("wbl_ivory_coast"),
            address_countries: document.getElementById("wbl_countries")
        };

        // Hide all address elements initially
        Object.values(addresses).forEach(address => address.style.display = 'none');

        // Show the selected address
        if (addresses[selectedAddressId]) {
            addresses[selectedAddressId].style.display = 'block';
        }
    },
});

export default publicWidget.registry.AddressHide;

