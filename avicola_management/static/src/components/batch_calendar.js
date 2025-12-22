/** @odoo-module **/

import { Component, useRef, onMounted, onWillUnmount } from "@odoo/owl";

export class BatchCalendar extends Component {
    static template = "avicola_management.BatchCalendar";
    static props = {
        lotes: Array,
    };

    setup() {
        this.calendarRef = useRef("calendar");
        this.calendar = null;

        onMounted(() => {
            this.initCalendar();
        });

        onWillUnmount(() => {
            if (this.calendar) {
                this.calendar.destroy();
            }
        });
    }

    initCalendar() {
        if (!this.calendarRef.el || !window.FullCalendar) return;

        const events = this.buildEvents();

        this.calendar = new window.FullCalendar.Calendar(this.calendarRef.el, {
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,listMonth'
            },
            height: '100%',
            locale: 'es',
            events: events,
            eventClick: (info) => {
                console.log("Event clicked:", info.event);
            },
            themeSystem: 'standard',
        });

        this.calendar.render();
    }

    buildEvents() {
        const events = [];
        this.props.lotes.forEach(lote => {
            // Ingreso
            if (lote.fecha_ingreso) {
                events.push({
                    title: `🐣 Ingreso ${lote.name}`,
                    start: lote.fecha_ingreso,
                    color: '#10b981', // Success
                    allDay: true,
                });

                // Proyección de Salida
                if (lote.fecha_salida_proyectada) {
                    events.push({
                        title: `🚛 Salida ${lote.name}`,
                        start: lote.fecha_salida_proyectada,
                        color: '#f59e0b', // Warning
                        allDay: true,
                    });
                }

                // Eventos simulados de ciclo (Vacunas, cambios de alimento)
                // En un caso real, esto vendría del modelo
                const ingreso = new Date(lote.fecha_ingreso);

                // Día 7: Vacuna 1
                const dia7 = new Date(ingreso);
                dia7.setDate(ingreso.getDate() + 7);
                events.push({
                    title: `💉 Vacuna Newcastle (${lote.name})`,
                    start: dia7.toISOString().split('T')[0],
                    color: '#6366f1', // Info
                });

                // Día 21: Cambio Alimento
                const dia21 = new Date(ingreso);
                dia21.setDate(ingreso.getDate() + 21);
                events.push({
                    title: `🍲 Cambio a Engorde (${lote.name})`,
                    start: dia21.toISOString().split('T')[0],
                    color: '#8b5cf6', // Purple
                });
            }
        });
        return events;
    }
}
