/** @odoo-module **/
import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets"
const { Component, onWillStart, useRef, onMounted, useEffect, onWillUnmount } =owl
import { useService } from "@web/core/utils/hooks"

export class ChartRenderer extends Component {
    setup(){
        this.chartRef = useRef('chart')
        this.actionService = useService('action')

        onWillStart(async ()=>{
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.3.0/chart.umd.min.js");
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.1/moment.min.js");
        })
        useEffect(()=>{
            this.renderChart()
        }, ()=>[this.props.config])
        onMounted(()=>this.renderChart())
        onWillUnmount(()=>{
            if (this.chart){
        this.chart.destroy()
    }
        })
    }
    renderChart() {
    if (this.chart){
        this.chart.destroy()
    }
    this.chart = new Chart(this.chartRef.el, {
        type: this.props.type,
        data: this.props.config.data,
        options: {
            onClick: (e) => {
                const active = e.chart.getActiveElements();
                if (active.length > 0 && active[0]) { // Check if active[0] is defined
                    const label = e.chart.data.labels[active[0].index];
                    const dataset = e.chart.data.datasets[active[0].datasetIndex].label;

                    const { label_field, domain } = this.props.config;
                    let new_domain = domain ? domain : [];

                    if (label_field) {
                        if (label_field.includes('date')) {
                            const timeStamp = Date.parse(label);
                            const selected_month = moment(timeStamp);
                            const month_start = selected_month.format('YYYY-MM-DD');
                            const month_end = selected_month.endOf('month').format('YYYY-MM-DD');
                            new_domain.push(['date', '>=', month_start], ['date', '<=', month_end]);
                        } else {
                            new_domain.push([label_field, '=', label]);
                        }
                    }
                    if (dataset == 'Quotations'){
                        new_domain.push(['state', 'in', ['draft', 'sent']])
                    }
                    if (dataset == 'Orders'){
                        new_domain.push(['state', 'in', ['sale', 'done']])
                    }

                    this.actionService.doAction({
                        type: "ir.actions.act_window",
                        name: this.props.title,
                        res_model: "sale.report",
                        domain: new_domain,
                        views: [
                            [false, "list"],
                            [false, "form"],
                        ]
                    });
                }
            },
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                },
                title: {
                    display: true,
                    text: this.props.title,
                    position: 'bottom',
                }
            },
            scales: 'scales' in this.props.config ? this.props.config.scales : {}
        },
    });
}


}

ChartRenderer.template = "owl.ChartRenderer"; // Update the template name if needed

