/** @odoo-module **/

import { Component } from "@odoo/owl";

export class KpiCard extends Component {
    static template = "avicola_management.KpiCard";
    static props = {
        title: String,
        value: [Number, String],
        icon: String,
        status: { type: String, optional: true },
        subtitle: { type: String, optional: true },
    };

    get statusClass() {
        const statusMap = {
            success: 'kpi-success',
            warning: 'kpi-warning',
            danger: 'kpi-danger',
            info: 'kpi-info',
        };
        return statusMap[this.props.status] || 'kpi-info';
    }
}
