/* @odoo-module */

import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";
import { renderToElement } from "@web/core/utils/render";
import { KeepLast } from "@web/core/utils/concurrency";
import { Component } from "@odoo/owl";


publicWidget.registry.PartialPayment = publicWidget.Widget.extend({
    selector: '#wbl_brand_search',
    events: {
        'click #wbl_btn_search': '_onClickSearch',
        'click #add_to_cart_wrap': 'onClickAddToCart',
    },

    init: function () {
        this._super.apply(this, arguments);
        this.validationPerformed = false;

    },

    _onClickSearch: function (ev) {
        console.log('working1')
        const searchText = $('#brand_search').val().toLowerCase();

        $('.brand_item').each(function () {
            const brandName = $(this).find('.card-title').text().toLowerCase();
            $(this).toggle(brandName.includes(searchText));
        });
    },

});
