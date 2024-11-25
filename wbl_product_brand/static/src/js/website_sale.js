/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";
import { renderToElement } from "@web/core/utils/render";
import { KeepLast } from "@web/core/utils/concurrency";
import { Component } from "@odoo/owl";
import { DatePicker, DateTimePicker } from "@web/core/datetime/datetime_picker";

publicWidget.registry.WebsiteSalePriceQuotation = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    events: {
        'click .selected_product_types': 'filter_website_product',
        'click .form-check-label': 'filter_website_product', // Trigger when label is clicked
    },
    init() {
        this._super(...arguments);
    },
    // Function to handle checkbox and label clicks
    filter_website_product: function (ev) {
        const selected_brands = document.querySelectorAll('.selected_product_types:checked');
        const selected_product_brands = Array.from(selected_brands).map(checkbox => checkbox.value);

        if (selected_product_brands.length > 0) {
            // Construct the URL based on the selected brands
            const brand_slug = selected_product_brands.join('-'); // Example: "brand1-brand2"
            const url = `/shop/brand/${brand_slug}`;
            window.location.href = url;  // Redirect to the constructed URL
        } else {
            window.location.href = '/shop';  // Fallback URL if no brands are selected
        }
    }
});
