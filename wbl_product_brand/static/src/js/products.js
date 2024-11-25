/* @odoo-module */

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.ProductSearch = publicWidget.Widget.extend({
        selector: '#wbl_brand_products_grid',
        events: {
            'click #wbl_prod_btn_search': '_onClickSearch',
            'keypress #prod_search': '_onEnterSearch',
            'change .filter-checkbox': '_onFilterChange',
            'change .attribute-filter-checkbox': '_onFilterChange'
        },

    init: function () {
        this._super.apply(this, arguments);
    },

    _onClickSearch: function (ev) {
        this._filterProducts();
    },

    _onEnterSearch: function (ev) {
        if (ev.which === 13) {
            this._filterProducts();
        }
    },

    _onFilterChange: function () {
        this._filterProducts();
    },

    _filterProducts: function () {
        const searchText = ($('#prod_search').val() || '').toLowerCase();
        const selectedTypes = $('.filter-checkbox:checked').map(function () {
            return $(this).val();
        }).get();
        const selectedAttributes = $('.attribute-filter-checkbox:checked').map(function () {
            return $(this).val();
        }).get();

        $('.prod_item').each(function () {
            const productName = $(this).find('.product-name').text().toLowerCase();
            const productType = $(this).data('type');
            const productAttributes = $(this).find('.product-attribute').map(function () {
                return $(this).text().toLowerCase();
            }).get();
            const nameMatches = productName.includes(searchText);

            const typeMatches = selectedTypes.length === 0 || selectedTypes.includes(productType);
            const attributesMatch = selectedAttributes.length === 0 || selectedAttributes.every(selectedAttr =>
                productAttributes.some(attr => attr.includes(selectedAttr.toLowerCase()))
            );
            $(this).toggle(nameMatches && typeMatches && attributesMatch);
        });
    },
});
