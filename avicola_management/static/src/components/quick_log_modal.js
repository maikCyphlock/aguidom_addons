/** @odoo-module **/

import { Component, useState } from "@odoo/owl";

export class QuickLogModal extends Component {
    static template = "avicola_management.QuickLogModal";
    static props = {
        type: String,  // 'mortalidad' | 'recoleccion'
        lotes: Array,
        selectedLoteId: { type: [Number, { value: null }], optional: true },
        onSubmit: Function,
        onClose: Function,
    };

    setup() {
        this.state = useState({
            loteId: this.props.selectedLoteId || null,
            cantidad: 1,
            causa: 'natural',
            clasificacion: 'grande',
        });
    }

    get title() {
        return this.props.type === 'mortalidad'
            ? '💀 Registrar Mortalidad'
            : '🥚 Registrar Recolección';
    }

    get isValid() {
        return this.state.loteId && this.state.cantidad > 0;
    }

    get filteredLotes() {
        if (this.props.type === 'recoleccion') {
            return this.props.lotes.filter(l => l.tipo_produccion === 'ponedora');
        }
        return this.props.lotes;
    }

    increment() {
        this.state.cantidad++;
    }

    decrement() {
        if (this.state.cantidad > 1) {
            this.state.cantidad--;
        }
    }

    incrementBy(amount) {
        this.state.cantidad += amount;
    }

    submit() {
        if (!this.isValid) return;

        this.props.onSubmit({
            loteId: this.state.loteId,
            cantidad: this.state.cantidad,
            causa: this.state.causa,
            clasificacion: this.state.clasificacion,
        });
    }

    close() {
        this.props.onClose();
    }
}
