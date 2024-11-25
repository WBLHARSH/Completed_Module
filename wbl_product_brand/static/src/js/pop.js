/* @odoo-module */
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.NotifyButton = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    events: {
        'click #wbl_notify': '_onButtonClick',
        'click .close': '_onCloseButtonClick'
    },
    _onButtonClick(ev) {

        $('#message_popup').modal('show');
    },
    _onCloseButtonClick(ev) {

        $('#message_popup').modal('hide');
    }
});

export default publicWidget.registry.NotifyButton;
