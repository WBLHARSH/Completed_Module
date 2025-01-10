/** @odoo-module **/

import publicWidget from '@web/legacy/js/public/public_widget';

publicWidget.registry.WblsearchBar = publicWidget.Widget.extend({
    selector: '.wbl-seller-product-search',
    events: {
        'click #wbl_search_seller_product': '_searchProduct',
    },

    /**
     * @constructor
     */
    init: function () {
        this._super.apply(this, arguments);
    },

    /**
     * Handle search button click and fetch input value
     */
    _searchProduct: function (ev) {
        ev.preventDefault(); // Prevent the default form submission
        const search = this.$el.find('.search-query').val().trim(); // Fetch and trim the input value

        if (search) {
             const currentUrl = new URL(window.location.href); // Get the current URL
             currentUrl.searchParams.set('search', search); // Set or update the "search" parameter
             window.location.href = currentUrl.toString(); // Redirect to the updated URL
        } else {
            console.log("Search field is empty.");
        }
    },
});

export default {
    searchBar: publicWidget.registry.WblsearchBar,
};
