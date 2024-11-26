/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import "@website_sale/js/website_sale";
import { _t } from "@web/core/l10n/translation";

publicWidget.registry.AddressHide = publicWidget.Widget.extend({
    selector: '#div_addresses',
    events: {
        'click .form-check-input': '_onButtonShowAddress',
    },
    start: function () {
        this._super.apply(this, arguments);
        this.rpc = this.bindService("rpc");

        const selectedAddressId = this.$('input[name="selected_option"]:checked').attr('id');
        if (selectedAddressId) {
            this._toggleAddressVisibility(selectedAddressId);
        }
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
    _toggleAddressVisibility(selectedAddressId) {
        const addresses = {
            address_abidjan: document.getElementById("wbl_abidjan"),
            address_ivory_coast: document.getElementById("wbl_ivory_coast"),
            address_countries: document.getElementById("wbl_countries")
        };

        // Hide all address elements initially
        Object.values(addresses).forEach(address => {
            if (address) {
                address.style.display = 'none';
                address.style.border = 'none';
            }
        });

        // Show the selected address if it exists
        if (addresses[selectedAddressId]) {
            addresses[selectedAddressId].style.display = 'block';
             const selectTag = addresses[selectedAddressId].querySelector('select');
            if (!selectTag.value || selectTag.value === "") {
                    selectTag.style.border = '1px solid red';
            }
        }
    },
});

export default publicWidget.registry.AddressHide;

