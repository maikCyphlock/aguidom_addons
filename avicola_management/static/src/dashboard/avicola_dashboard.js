/** @odoo-module **/
/*
    Avícola Management Dashboard
    Main OWL Component for Real-time Poultry Farm Management
*/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart, onMounted, useRef } from "@odoo/owl";

// Import sub-components
import { KpiCard } from "../components/kpi_card";
import { BarnCard } from "../components/barn_card";
import { QuickLogModal } from "../components/quick_log_modal";
import { BatchCalendar } from "../components/batch_calendar";

export class AvicolaDashboard extends Component {
    static template = "avicola_management.Dashboard";
    static components = { KpiCard, BarnCard, QuickLogModal, BatchCalendar };
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.action = useService("action");

        this.chartRef = useRef("growthChart");
        this.conversionChartRef = useRef("conversionChart");

        this.state = useState({
            galpones: [],
            alimentos: [],
            kpis: {
                totalAves: 0,
                mortalidadPromedio: 0,
                consumoAlimentoDiario: 0,
                huevosHoy: 0,
            },
            loteSeleccionado: null,
            activeTab: 'overview',
            showQuickLog: false,
            quickLogType: 'mortalidad', // 'mortalidad' | 'recoleccion'
            loading: true,
            alertas: [],
        });

        onWillStart(async () => {
            await this.loadData();
        });

        onMounted(() => {
            this.initCharts();
        });
    }

    async loadData() {
        this.state.loading = true;
        try {
            // Load galpones with active lots
            const galpones = await this.orm.searchRead(
                "avicola.galpon",
                [["active", "=", true]],
                [
                    "name", "capacidad", "aves_actuales", "temperatura_actual",
                    "humedad_actual", "estado_sanitario", "porcentaje_ocupacion",
                    "mortalidad_acumulada", "lote_activo_id"
                ]
            );

            // Load active lots for more details
            const lotes = await this.orm.searchRead(
                "avicola.lote",
                [["state", "=", "activo"]],
                [
                    "name", "galpon_id", "raza", "edad_dias", "cantidad_actual",
                    "cantidad_inicial", "porcentaje_mortalidad", "progreso_ciclo",
                    "dias_para_salida", "peso_actual_promedio", "tipo_produccion"
                ]
            );

            // Load feed inventory
            const alimentos = await this.orm.searchRead(
                "avicola.alimento",
                [["active", "=", true]],
                ["name", "tipo", "stock_kg", "stock_minimo", "estado", "dias_stock_restante"]
            );

            // Compute KPIs
            const totalAves = galpones.reduce((sum, g) => sum + g.aves_actuales, 0);
            const mortalidadPromedio = galpones.length > 0
                ? galpones.reduce((sum, g) => sum + g.mortalidad_acumulada, 0) / galpones.length
                : 0;

            // Build alerts
            const alertas = [];
            galpones.forEach(g => {
                if (g.estado_sanitario === 'critico') {
                    alertas.push({
                        type: 'danger',
                        icon: '🚨',
                        message: `${g.name}: Estado crítico - Mortalidad alta`,
                    });
                } else if (g.estado_sanitario === 'alerta') {
                    alertas.push({
                        type: 'warning',
                        icon: '⚠️',
                        message: `${g.name}: Alerta de temperatura o mortalidad`,
                    });
                }
            });

            alimentos.forEach(a => {
                if (a.estado === 'critico' || a.estado === 'agotado') {
                    alertas.push({
                        type: 'danger',
                        icon: '📦',
                        message: `${a.name}: Stock crítico (${a.stock_kg.toFixed(1)} kg)`,
                    });
                } else if (a.estado === 'bajo') {
                    alertas.push({
                        type: 'warning',
                        icon: '📦',
                        message: `${a.name}: Stock bajo`,
                    });
                }
            });

            // Attach lote info to galpones
            const galponesConLote = galpones.map(g => {
                const lote = lotes.find(l => l.galpon_id && l.galpon_id[0] === g.id);
                return { ...g, lote };
            });

            this.state.galpones = galponesConLote;
            this.state.alimentos = alimentos;
            this.state.lotes = lotes;
            this.state.kpis = {
                totalAves,
                mortalidadPromedio,
                consumoAlimentoDiario: 0, // Placeholder for future sensor integration
                huevosHoy: 0, // Placeholder
            };
            this.state.alertas = alertas;

        } catch (error) {
            this.notification.add("Error cargando datos del dashboard", {
                type: "danger",
            });
            console.error(error);
        }
        this.state.loading = false;
    }

    initCharts() {
        // Initialize weight chart
        if (this.chartRef.el && window.Chart) {
            const ctx = this.chartRef.el.getContext('2d');
            this.growthChart = new window.Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['Día 1', 'Día 7', 'Día 14', 'Día 21', 'Día 28', 'Día 35', 'Día 42'],
                    datasets: [
                        {
                            label: 'Peso Real (g)',
                            data: [42, 180, 460, 920, 1480, 2100, 2800],
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            tension: 0.3,
                            fill: true,
                        },
                        {
                            label: 'Peso Guía Ross 308 (g)',
                            data: [42, 195, 500, 990, 1580, 2260, 3000],
                            borderColor: '#6366f1',
                            borderDash: [5, 5],
                            tension: 0.3,
                            fill: false,
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: { color: '#94a3b8' }
                        },
                        title: {
                            display: true,
                            text: 'Curva de Crecimiento',
                            color: '#f1f5f9'
                        }
                    },
                    scales: {
                        x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                        y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                    }
                }
            });
        }

        // Initialize conversion chart
        if (this.conversionChartRef.el && window.Chart) {
            const ctx = this.conversionChartRef.el.getContext('2d');
            this.conversionChart = new window.Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4', 'Sem 5', 'Sem 6'],
                    datasets: [{
                        label: 'Conversión Alimenticia',
                        data: [1.1, 1.25, 1.42, 1.58, 1.72, 1.85],
                        backgroundColor: [
                            '#10b981', '#10b981', '#f59e0b', '#f59e0b', '#ef4444', '#ef4444'
                        ],
                        borderRadius: 4,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        title: {
                            display: true,
                            text: 'Conversión Alimenticia Semanal',
                            color: '#f1f5f9'
                        }
                    },
                    scales: {
                        x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
                        y: {
                            ticks: { color: '#94a3b8' },
                            grid: { color: '#334155' },
                            suggestedMin: 1,
                            suggestedMax: 2.5
                        }
                    }
                }
            });
        }
    }

    getMortalityStatus(percent) {
        if (percent > 5) return 'danger';
        if (percent > 2) return 'warning';
        return 'success';
    }

    openQuickLog(type, loteId = null) {
        this.state.quickLogType = type;
        this.state.loteSeleccionado = loteId;
        this.state.showQuickLog = true;
    }

    closeQuickLog() {
        this.state.showQuickLog = false;
        this.state.loteSeleccionado = null;
    }

    async onQuickLogSubmit(data) {
        try {
            if (this.state.quickLogType === 'mortalidad') {
                await this.orm.call(
                    "avicola.mortalidad",
                    "registrar_rapido",
                    [data.loteId, data.cantidad, data.causa || 'natural']
                );
                this.notification.add(`Mortalidad registrada: ${data.cantidad} aves`, {
                    type: "success",
                });
            } else {
                await this.orm.call(
                    "avicola.recoleccion",
                    "registrar_rapido",
                    [data.loteId, data.cantidad, data.clasificacion || 'grande']
                );
                this.notification.add(`Recolección registrada: ${data.cantidad} huevos`, {
                    type: "success",
                });
            }
            this.closeQuickLog();
            await this.loadData(); // Refresh data
        } catch (error) {
            this.notification.add("Error al registrar", { type: "danger" });
            console.error(error);
        }
    }

    openGalpon(galponId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "avicola.galpon",
            res_id: galponId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    openLote(loteId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "avicola.lote",
            res_id: loteId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    startTour() {
        if (!window.driver) {
            console.error("Driver.js not loaded");
            return;
        }

        const driverObj = window.driver.js.driver({
            showProgress: true,
            steps: [
                { element: '.dashboard-header h1', popover: { title: 'Bienvenido', description: 'Este es tu centro de comando avícola.' } },
                { element: '.kpi-grid', popover: { title: 'KPIs en Tiempo Real', description: 'Monitorea el estado general de toda la granja aquí.' } },
                { element: '.galpones-section', popover: { title: 'Galpones', description: 'Cada tarjeta representa un galpón. Ves rápidamente su estado sanitario y edad del lote.' } },
                { element: '.fab-main', popover: { title: 'Acción Rápida', description: 'Usa este botón para registrar mortalidad o huevos sin navegar.' } },
                { element: '.nav-btn-calendar', popover: { title: 'Nuevo: Calendario', description: 'Planifica vacunas y salidas en la vista de calendario.' } },
            ]
        });

        driverObj.drive();
    }

    switchTab(tab) {
        this.state.activeTab = tab;
        if (tab === 'overview') {
            // Re-init charts when switching back to overview if needed, 
            // but for now keeping them in DOM with v-show/t-if logic might be handled by template
            setTimeout(() => this.initCharts(), 100);
        }
    }

    async refreshData() {
        await this.loadData();
        this.notification.add("Datos actualizados", { type: "info" });
    }
}

registry.category("actions").add("avicola_management.dashboard", AvicolaDashboard);
