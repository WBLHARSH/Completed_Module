/** @odoo-module */
import PublicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from '@web/core/network/rpc_service';

export const websiteSaleDeliverySave = PublicWidget.Widget.extend({
    selector: "#schedule_delivery",

    start() {
        $('button[name="o_payment_submit_button"]').bind("click",function(ev){
            var order_message_field = $('#note_field_id').val();
            var desire_date_field = $('#wbl_desire_date').val();
            jsonrpc("/save_delivery/",{
                'order_message_field': order_message_field,
                'desire_date_field': desire_date_field
            });
        });
    },

});

PublicWidget.registry.websiteSaleDeliverySave =  websiteSaleDeliverySave;
