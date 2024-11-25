/** @odoo-module **/
import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets"
import { ChartRenderer } from "./chart_renderer/chart_renderer"
import { useService } from "@web/core/utils/hooks"
const { Component, onWillStart, useRef, onMounted, useState } = owl


export class OwlSalesDashboard extends Component {

    // top product
    async getTopProducts(){
        let domain = [['state', 'in', ['sale', 'done']]]
        if (this.state.period > 0){
            domain.push(['date','>', this.state.current_date])
        }
        const data = await this.orm.readGroup('sale.report', domain, ['product_id','price_total'], ['product_id'],{
        limit: 5, orderby: "price_total desc"})
        this.state.topProducts = {
            data: {
                     labels: data.map(d=>d.product_id[1]),
                      datasets: [{
                        label: 'Total',
                        data: data.map(d=>d.price_total),
                        hoverOffset: 4,
                      },
                      {
                        label: 'Count',
                        data: data.map(d=>d.product_id_count),
                        hoverOffset: 4,
                      }]
                  },
                  domain,
                  label_field: 'product_id',
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
        quotations:{
            value:12,
            percentage:8,
        },
        period:90,
      })
      this.orm = useService('orm')
      this.actionService = useService('action')

      onWillStart(async ()=>{
        await loadJS("https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.1/moment.min.js");
        this.getDates()
        await this.getQuotations()
        await this.getOrders()
        await this.getTopProducts()
        await this.getTopSalesPeople()
        await this.getMonthlySales()
        await this.getPartnerOrders()
      })
    }
    async onChangePeriod(){
        this.getDates()
        await this.getQuotations()
        await this.getOrders()
        await this.getTopProducts()
        await this.getTopSalesPeople()
        await this.getMonthlySales()
        await this.getPartnerOrders()

    }
    getDates(){
        this.state.current_date = moment().subtract(this.state.period, 'days').format('YYYY-MM-DD');
        this.state.previous_date = moment().subtract(this.state.period * 2, 'days').format('YYYY-MM-DD');
    }
    async getQuotations(){
        let domain = [['state', 'in', ['approved']]]
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.current_date])
        }
        const data = await this.orm.searchCount("mp.seller.product", domain)
        this.state.quotations.value = data

        //Previous Period
        let prev_domain = [['state', 'in', ['approved']]]
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.previous_date],['create_date','<=', this.state.current_date])
        }
        const prev_data = await this.orm.searchCount("mp.seller.product", prev_domain)
        const percentage = ((data - prev_data)/prev_data)*100
        this.state.quotations.percentage = percentage.toFixed(2)

    }
    async getOrders(){
    let domain = [['state', 'in', ['sale', 'done']]]
    if (this.state.period > 0){
        domain.push(['date_order','>', this.state.current_date])
    }
    const data = await this.orm.searchCount("sale.order", domain)

    // Previous Period
    let prev_domain = [['state', 'in', ['sale', 'done']]]
    if (this.state.period > 0){
        prev_domain.push(['date_order','>', this.state.previous_date], ['date_order','<=', this.state.current_date])
    }
    const prev_data = await this.orm.searchCount("sale.order", prev_domain)
    const percentage = prev_data ? ((data - prev_data) / prev_data) * 100 : 0

    // Revenues
    const current_revenue = await this.orm.readGroup('sale.order', domain, ['amount_total:sum'], [])
    const prev_revenue = await this.orm.readGroup('sale.order', prev_domain, ['amount_total:sum'], [])
    const current_amount_total = current_revenue[0]?.amount_total || 0
    const prev_amount_total = prev_revenue[0]?.amount_total || 0
    const revenue_percentage = prev_amount_total ? ((current_amount_total - prev_amount_total) / prev_amount_total) * 100 : 0

    // Average
    const avg_current_average = await this.orm.readGroup('sale.order', domain, ['amount_total:avg'], [])
    const avg_prev_average = await this.orm.readGroup('sale.order', prev_domain, ['amount_total:avg'], [])
    const avg_current_amount_total = avg_current_average[0]?.amount_total || 0
    const avg_prev_amount_total = avg_prev_average[0]?.amount_total || 0
    const average_percentage = avg_prev_average ? ((avg_current_amount_total - avg_prev_amount_total) / avg_prev_amount_total) * 100 : 0

    this.state.orders = {
        value: data,
        percentage: percentage.toFixed(2),
        revenue: `$${(current_amount_total/1000).toFixed(2)}K`,
        revenue_percentage: revenue_percentage.toFixed(2),
        average: `$${(avg_current_amount_total/1000).toFixed(2)}K`,
        average_percentage: average_percentage.toFixed(2),
    }
}
    async viewQuotations(){
        let domain = [['state', 'in', ['approved']]]
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.current_date])
        }
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Marketplace Product",
            res_model: "mp.seller.product",
            domain,
            views: [
                [false, "kanban"],
                [false, "form"]
            ]
        });

    }
    viewOrders(){
    let domain = [['state', 'in', ['sale', 'done']]];
    if (this.state.period > 0) {
        domain.push(['date_order', '>', this.state.current_date]);
    }

    this.actionService.doAction({
        type: "ir.actions.act_window",
        name: "Marketplace Product",
        res_model: "mp.seller.product",
        domain,
        context: { group_by: ['create_date'] },
        views: [
            [false, "list"],
            [false, "form"]
        ]
    });
}
    viewRevenues(){
    let domain = [['state', 'in', ['sale', 'done']]];
    if (this.state.period > 0) {
        domain.push(['date_order', '>', this.state.current_date]);
    }

    this.actionService.doAction({
        type: "ir.actions.act_window",
        name: "Quotations",
        res_model: "sale.order",
        domain,
        context: { group_by: ['date_order'] },
        views: [
            [false, "pivot"],
            [false, "form"]
        ]
    });
}


}

OwlSalesDashboard.template = "owl.OwlSalesDashBoard"; // Update the template name if needed
OwlSalesDashboard.components = { ChartRenderer }; // Update the template name if needed

// Registering the action
registry.category("actions").add("owl.sales_dashboard", OwlSalesDashboard);
