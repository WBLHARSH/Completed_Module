/** @odoo-module **/
import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets"
import { ChartRenderer } from "./chart_renderer/chart_renderer"
import { useService } from "@web/core/utils/hooks"
const { Component, onWillStart, useRef, onMounted, useState } = owl

export class OwlSalesDashboard extends Component {

    // top product
    async getTopProducts(){
        let domain = [['state', 'in', ['sale', 'done']], ['seller_id', '!=', false]]
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.current_date])
        }
        const data = await this.orm.readGroup('sale.order.line', domain, ['id','price_total'], ['seller_id'],{
        limit: 5, orderby: "price_total desc"})
        this.state.topProducts = {
            data: {
                     labels: data.map(d=>d.seller_id[1]),
                      datasets: [{
                        label: 'Total',
                        data: data.map(d=>d.price_total),
                        hoverOffset: 4,
                      },
                      {
                        label: 'Count',
                        data: data.map(d=>d.seller_id_count),
                        hoverOffset: 4,
                      }]
                  },
                  domain,
                  label_field: 'seller_id',
        }
    }
    // top sales people
    async getTopSalesPeople(){
        let domain = [['state', 'in', ['sale', 'done']]]
        if (this.state.period > 0){
            domain.push(['date','>', this.state.current_date])
        }
        const data = await this.orm.readGroup('sale.report', domain, ['user_id','price_total'], ['user_id'],{
        limit: 5, orderby: "price_total desc"})
        this.state.topSalesPeople = {
            data: {
                     labels: data.map(d=>d.user_id[1]),
                      datasets: [{
                        label: 'Total',
                        data: data.map(d=>d.price_total),
                        hoverOffset: 4,
                      },
                      ]
                  },
                  domain,
                  label_field: 'user_id',
        }
    }
    // monthly sales
    async getMonthlySales(){
        let domain = [['state', 'in', ['draft','sent','sale', 'done']]]
        if (this.state.period > 0){
            domain.push(['date','>', this.state.current_date])
        }
        const data = await this.orm.readGroup('sale.report', domain, ['date','state','price_total'], ['date','state'],{orderby: "date",lazy:false})
        this.state.monthlySales = {
            data: {
                     labels: [... new Set(data.map(d=>d.date))],
                      datasets: [{
                        label: 'Quotations',
                        data: data.filter(d => d.state == 'draft' || d.state == 'sent' ).map(d=>d.price_total),
                        hoverOffset: 4,
                        backgroundColor:"red"
                      },
                      {
                        label: 'Orders',
                        data: data.filter(d => ['sale', 'done'].includes(d.state)).map(d=>d.price_total),
                        hoverOffset: 4,
                        backgroundColor:"green"

                      },
                      ]
                  },
                  domain,
                  label_field: 'date',
        }
    }
    // partner orders
    async getPartnerOrders(){
        let domain = [['state', 'in', ['draft','sent','sale', 'done']]]
        if (this.state.period > 0){
            domain.push(['date','>', this.state.current_date])
        }
        const data = await this.orm.readGroup('sale.report', domain, ['partner_id','price_total','product_uom_qty'], ['partner_id'],{orderby: "partner_id",lazy:false})
        this.state.partnerOrders = {
            data: {
                     labels: data.map(d=>d.partner_id[1]),
                      datasets: [{
                        label: 'Total Amount',
                        data: data.map(d=>d.price_total),
                        hoverOffset: 4,
                        backgroundColor:"orange",
                        yAxisID:'Total',
                        order:1,
                      },
                      {
                        label: 'Ordered Qty',
                        data: data.map(d=>d.product_uom_qty),
                        hoverOffset: 4,
                        backgroundColor:"blue",
                        type:'line',
                        borderColor:"blue",
                        yAxisID:'Qty',
                        order:0,

                      }]
                  },
                  domain,
                  label_field: 'partner_id',
            sacles: {
                Qty: {
                    position: 'right',
                }
            }
        }
    }

    setup(){
      this.state =useState({
       isAdmin: false,
        quotations:{
            value:12,
            percentage:8,
            draft:8,
            pending:8,
            approved:8,
            denied:8,
        },
        period:90,
      })
      this.orm = useService('orm')
      this.actionService = useService('action')
      this.rpc = useService('rpc')
      onWillStart(async ()=>{
        await loadJS("https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.1/moment.min.js");
        this.getDates()
        await this.getQuotations()
        await this.getLineOrders()
        await this.getDeliveryOrders()
        await this.getPaymentRequest()
        await this.getSellerRevenue()
        await this.getOrders()
        await this.getTopProducts()
        await this.getTopSalesPeople()
        await this.getMonthlySales()
        await this.getPartnerOrders()
        const response = await this.rpc('/custom_dashboard/user_groups', {});
        this.state.isAdmin = response.is_admin;
        this.state.currency_symbol = response.currency_symbol;
      })
    }

    async onChangePeriod(){
        this.getDates()
        await this.getQuotations()
        await this.getLineOrders()
        await this.getDeliveryOrders()
        await this.getPaymentRequest()
        await this.getOrders()
        await this.getTopProducts()
        await this.getTopSalesPeople()
        await this.getMonthlySales()
        await this.getPartnerOrders()
        await this.getSellerRevenue()


    }

    getDates(){
        this.state.current_date = moment().subtract(this.state.period, 'days').format('YYYY-MM-DD');
        this.state.previous_date = moment().subtract(this.state.period * 2, 'days').format('YYYY-MM-DD');
    }

    async getQuotations() {
    let domain = [['state', 'in', ['approved','draft','pending','denied']]];
    let draft_domain = [['state', 'in', ['draft']]];
    let pending_domain = [['state', 'in', ['pending']]];
    let approved_domain = [['state', 'in', ['approved']]];
    let denied_domain = [['state', 'in', ['denied']]];

    if (this.state.period > 0) {
        domain.push(['create_date', '>', this.state.current_date]);
    }

    // Current Period
    const data = await this.orm.searchCount("mp.seller.product", domain);
    const draft = await this.orm.searchCount("mp.seller.product", draft_domain);
    const pending = await this.orm.searchCount("mp.seller.product", pending_domain);
    const approved = await this.orm.searchCount("mp.seller.product", approved_domain);
    const denied = await this.orm.searchCount("mp.seller.product", denied_domain);

    // Previous Period
    const prev_domain = [['state', 'in', ['approved','draft','pending','denied']], ['create_date', '>', this.state.previous_date], ['create_date', '<=', this.state.current_date]];
    const prev_draft_domain = [...draft_domain, ['create_date', '>', this.state.previous_date], ['create_date', '<=', this.state.current_date]];
    const prev_pending_domain = [...pending_domain, ['create_date', '>', this.state.previous_date], ['create_date', '<=', this.state.current_date]];
    const prev_approved_domain = [...approved_domain, ['create_date', '>', this.state.previous_date], ['create_date', '<=', this.state.current_date]];
    const prev_denied_domain = [...denied_domain, ['create_date', '>', this.state.previous_date], ['create_date', '<=', this.state.current_date]];

    const prev_data = await this.orm.searchCount("mp.seller.product", prev_domain);
    const prev_draft = await this.orm.searchCount("mp.seller.product", prev_draft_domain);
    const prev_pending = await this.orm.searchCount("mp.seller.product", prev_pending_domain);
    const prev_approved = await this.orm.searchCount("mp.seller.product", prev_approved_domain);
    const prev_denied = await this.orm.searchCount("mp.seller.product", prev_denied_domain);

    this.state.quotations.value = data;
    this.state.quotations.draft = draft;
    this.state.quotations.pending = pending;
    this.state.quotations.approved = approved;
    this.state.quotations.denied = denied;

    this.state.quotations.previous = prev_data;
    this.state.quotations.draft_previous = prev_draft;
    this.state.quotations.pending_previous = prev_pending;
    this.state.quotations.approved_previous = prev_approved;
    this.state.quotations.denied_previous = prev_denied;
}

    async getOrders(){
        let domain = [['state', 'in', ['approved','draft','pending','denied']]]
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.current_date])
        }
        const data = await this.orm.searchCount("marketplace.seller", domain)

        // Previous Period
        let prev_domain = [['state', 'in', ['approved','draft','pending','denied']]]
        if (this.state.period > 0){
            prev_domain.push(['create_date','>', this.state.previous_date], ['create_date','<=', this.state.current_date])
        }
        const prev_data = await this.orm.searchCount("marketplace.seller", prev_domain)
        const draft = await this.orm.searchCount("marketplace.seller", [['state', 'in', ['draft']]])
        const pending = await this.orm.searchCount("marketplace.seller", [['state', 'in', ['pending']]])
        const approved = await this.orm.searchCount("marketplace.seller", [['state', 'in', ['approved']]])
        const denied = await this.orm.searchCount("marketplace.seller", [['state', 'in', ['denied']]])

        this.state.orders = {
            value: data,
            draft: draft,
            pending: pending,
            approved: approved,
            denied: denied,
        }
    }

    async getLineOrders(){
        let domain = [['mp_state', 'in', ['approved','draft','pending','denied']], ['seller_id', '!=', false]]
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.current_date])
        }
        const data = await this.orm.searchCount("sale.order.line", domain)
        const draft = await this.orm.searchCount("sale.order.line", [['mp_state', 'in', ['draft']], ['seller_id', '!=', false]])
        const pending = await this.orm.searchCount("sale.order.line", [['mp_state', 'in', ['pending']], ['seller_id', '!=', false]])
        const approved = await this.orm.searchCount("sale.order.line", [['mp_state', 'in', ['approved']], ['seller_id', '!=', false]])
        const denied = await this.orm.searchCount("sale.order.line", [['mp_state', 'in', ['denied']], ['seller_id', '!=', false]])

        //Previous Period
        let prev_domain = [['state', 'in', ['approved','draft','pending','denied']],['seller_id', '!=', false]]
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.previous_date],['create_date','<=', this.state.current_date])
        }

        this.state.Saleorder = {
            value: data,
            draft: draft,
            pending: pending,
            approved: approved,
            denied: denied,
        }

    }

    async getDeliveryOrders(){
        let domain = [['state', 'in', ['draft','waiting','confirmed','assigned', 'done','cancel']], ['seller_id', '!=', false]]
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.current_date])
        }
        const data = await this.orm.searchCount("stock.picking", domain)
        const draft = await this.orm.searchCount("stock.picking", [['state', 'in', ['draft']] , ['seller_id', '!=', false]])
        const waiting = await this.orm.searchCount("stock.picking", [['state', 'in', ['waiting']], ['seller_id', '!=', false]])
        const ready = await this.orm.searchCount("stock.picking", [['state', 'in', ['assigned']], ['seller_id', '!=', false]])
        const done = await this.orm.searchCount("stock.picking", [['state', 'in', ['done']], ['seller_id', '!=', false]])

        //Previous Period
        let prev_domain = [['state', 'in', ['draft','waiting','confirmed','assigned', 'done','cancel']], ['seller_id', '!=', false]]
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.previous_date],['create_date','<=', this.state.current_date])
        }

        this.state.DeliveryOrder = {
            value: data,
            draft: draft,
            waiting: waiting,
            ready: ready,
            done: done,
        }

    }

    async getSellerRevenue(){
        let domain = [['state', 'in', ['approved']], ['seller_id', '!=', false],['payment_type', 'in', ['credit']]]
        let admin_domain = [['mp_state', 'in', ['approved']], ['seller_id', '!=', false],['state', 'in', ['sale','done']]]
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.current_date])
        }
        const payments = await this.orm.searchRead("marketplace.seller.payment", domain, ['payment_amount']);
        const data = payments.reduce((sum, record) => sum + (record.payment_amount || 0), 0);

        const admin_payments = await this.orm.searchRead("sale.order.line", admin_domain, ['admin_commission']);
        const admin_data = admin_payments.reduce((sum, record) => sum + (record.admin_commission || 0), 0);

        const draft = await this.orm.searchCount("marketplace.seller.payment", [['state', 'in', ['draft']],['payment_type', 'in', ['debit']]])
        const pending = await this.orm.searchCount("marketplace.seller.payment", [['state', 'in', ['pending']],['payment_type', 'in', ['debit']]])
        const approved = await this.orm.searchCount("marketplace.seller.payment", [['state', 'in', ['approved']],['payment_type', 'in', ['debit']]])
        const denied = await this.orm.searchCount("marketplace.seller.payment", [['state', 'in', ['denied']],['payment_type', 'in', ['debit']]])

        //Previous Period
        let prev_domain = [['state', 'in', ['approved']], ['seller_id', '!=', false],['payment_type', 'in', ['credit']]]
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.previous_date],['create_date','<=', this.state.current_date])
        }


        this.state.revenue = {
            value: data,
            admin_value: parseFloat(admin_data).toFixed(2),
            draft: draft,
            pending: pending,
            approved: approved,
            denied: denied,
        }

    }

    async getPaymentRequest(){
        let domain = [['state', 'in', ['draft','pending','approved','denied']],['payment_type', 'in', ['debit']]]
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.current_date])
        }
        const data = await this.orm.searchCount("marketplace.seller.payment", domain)

        // Previous Period
        let prev_domain = [['state', 'in', ['draft','pending','approved','denied']],['payment_type', 'in', ['debit']]]
        if (this.state.period > 0){
            prev_domain.push(['create_date','>', this.state.previous_date], ['create_date','<=', this.state.current_date])
        }
        const prev_data = await this.orm.searchCount("marketplace.seller.payment", prev_domain)
        const draft = await this.orm.searchCount("marketplace.seller.payment", [['state', 'in', ['draft']],['payment_type', 'in', ['debit']]])
        const pending = await this.orm.searchCount("marketplace.seller.payment", [['state', 'in', ['pending']],['payment_type', 'in', ['debit']]])
        const approved = await this.orm.searchCount("marketplace.seller.payment", [['state', 'in', ['approved']],['payment_type', 'in', ['debit']]])
        const denied = await this.orm.searchCount("marketplace.seller.payment", [['state', 'in', ['denied']],['payment_type', 'in', ['debit']]])

        this.state.pay_req = {
            value: data,
            draft: draft,
            pending: pending,
            approved: approved,
            denied: denied,
        }
    }

    async viewQuotations(){
        let domain =[['state', 'in', ['approved','draft','pending','denied']]]
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.current_date])
        }
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Marketplace Product",
            res_model: "mp.seller.product",
//            context: { group_by: ['create_date']},
            domain,
            views: [
                [false, "kanban"],
                [false, "form"]
            ]
        });

    }

    viewOrders(){
    let domain = [['state', 'in', ['approved','draft','pending','denied']]];
    if (this.state.period > 0) {
        domain.push(['create_date', '>', this.state.current_date]);
    }

    this.actionService.doAction({
        type: "ir.actions.act_window",
        name: "Marketplace Sellers",
        res_model: "marketplace.seller",
        domain,
//        context: { group_by: ['create_date'] },
        views: [
             [false, "kanban"],
            [false, "form"]
        ]
    });
}

    viewSaleOrder(){
    let domain = [['mp_state', 'in', ['approved','draft','pending','denied']], ['seller_id', '!=', false]]
    if (this.state.period > 0) {
        domain.push(['create_date', '>', this.state.current_date]);
    }

    this.actionService.doAction({
        type: "ir.actions.act_window",
        name: "Marketplace Order",
        res_model: "sale.order.line",
        domain,
        views: [
            [false, "kanban"],
            [false, "form"]
        ]
    });
}

    viewDeliveryOrder(){
     let domain = [['state', 'in', ['draft','waiting','confirmed','assigned', 'done','cancel']], ['seller_id', '!=', false]]
    if (this.state.period > 0) {
        domain.push(['create_date', '>', this.state.current_date]);
    }

    this.actionService.doAction({
        type: "ir.actions.act_window",
        name: "Marketplace Delivery Order",
        res_model: "stock.picking",
        domain,
        views: [
            [false, "kanban"],
            [false, "form"]
        ]
    });
}

    viewPaymentRequest(){
     let domain =  [['state', 'in', ['draft','pending','approved','denied']],['payment_type', 'in', ['debit']]]
    if (this.state.period > 0) {
        domain.push(['create_date', '>', this.state.current_date]);
    }

    this.actionService.doAction({
        type: "ir.actions.act_window",
        name: "Marketplace Seller Payments",
        res_model: "marketplace.seller.payment",
        domain,
        views: [
            [false, "list"],
            [false, "form"]
        ]
    });
}

    viewSellerPayment(){
        let domain = [['state', 'in', ['approved','draft','pending','denied']], ['seller_id', '!=', false]]
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.current_date]);
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Marketplace Seller Payment",
            res_model: "marketplace.seller.payment",
//            context: { group_by: ['create_date'] },
            domain,
            views: [
                [false, "tree"],
                [false, "form"]
            ]
        });
    }
}

OwlSalesDashboard.template = "owl.OwlSalesDashBoard"; // Update the template name if needed
OwlSalesDashboard.components = { ChartRenderer }; // Update the template name if needed

// Registering the action
registry.category("actions").add("owl.sales_dashboard", OwlSalesDashboard);
