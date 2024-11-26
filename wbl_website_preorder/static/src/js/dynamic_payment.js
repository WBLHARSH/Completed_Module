/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";


publicWidget.registry.DynamicPayment = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    events: {
        'input #vol': '_onButtonClick', // Use 'input' for real-time updates
    },
    _onButtonClick(ev){
        const rangeInput = document.getElementById('vol');
        const rangeValue = document.getElementById('rangeValue');
        if (rangeInput && rangeValue) {
            rangeValue.textContent = rangeInput.value;
        }
    }
});

export default publicWidget.registry.DynamicPayment;
