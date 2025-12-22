/** @odoo-module **/

import { Component } from "@odoo/owl";

export class BarnCard extends Component {
    static template = "avicola_management.BarnCard";
    static props = {
        galpon: Object,
        onOpenGalpon: { type: Function, optional: true },
        onOpenLote: { type: Function, optional: true },
        onQuickLog: { type: Function, optional: true },
    };

    get statusClass() {
        const status = this.props.galpon.estado_sanitario;
        const map = {
            optimo: 'status-optimo',
            alerta: 'status-alerta',
            critico: 'status-critico',
        };
        return map[status] || '';
    }

    get statusLabel() {
        const labels = {
            optimo: 'Óptimo',
            alerta: 'En Alerta',
            critico: 'Crítico',
        };
        return labels[this.props.galpon.estado_sanitario] || '';
    }

    get lote() {
        return this.props.galpon.lote;
    }

    get hasLote() {
        return !!this.lote;
    }

    get progressStyle() {
        const progress = this.lote?.progreso_ciclo || 0;
        return `width: ${progress}%`;
    }

    openGalpon() {
        if (this.props.onOpenGalpon) {
            this.props.onOpenGalpon(this.props.galpon.id);
        }
    }

    openLote() {
        if (this.props.onOpenLote && this.lote) {
            this.props.onOpenLote(this.lote.id);
        }
    }

    registrarMortalidad() {
        if (this.props.onQuickLog && this.lote) {
            this.props.onQuickLog('mortalidad', this.lote.id);
        }
    }
}
