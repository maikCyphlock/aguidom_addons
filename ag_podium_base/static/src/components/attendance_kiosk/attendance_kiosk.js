/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart } from "@odoo/owl";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

export class AttendanceKiosk extends Component {
    static template = "ag_podium_base.AttendanceKiosk";
    static props = { ...standardActionServiceProps };

    setup() {
        this.lol = useState({
            pile: []
        })
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            date: new Date().toISOString().split('T')[0],
            categories: [],
            selectedCategoryId: false,
            athletes: [],
            loading: false,
        });

        onWillStart(async () => {
            await this.loadCategories();
            await this.loadAthletes();
            await this.loadPile()
        });
    }
    async loadPile() {
        this.lol.pile = await this.orm.searchRead("podium.athlete", [['category_id.name', '=', 'compota']], [])
        console.log(this.lol)
    }
    async loadCategories() {
        this.state.categories = await this.orm.searchRead("podium.category", [], ["id", "name"]);

    }

    async loadAthletes() {
        this.state.loading = true;
        const domain = [['active', '=', true]];
        if (this.state.selectedCategoryId) {
            domain.push(['category_id', '=', this.state.selectedCategoryId]);
        }

        const athletes = await this.orm.searchRead("podium.athlete", domain, ["id", "name", "image_128", "category_id", "representative_id"]);

        console.log({ athletes })
        // Initialize status for each athlete (default: present)
        this.state.athletes = athletes.map(a => ({
            ...a,
            status: 'present' // 'present', 'absent', 'excused'
        }));
        this.state.loading = false;
    }

    async onCategoryChange(ev) {
        console.log(ev.target.value)
        this.state.selectedCategoryId = ev.target.value;
        return await this.loadAthletes();
    }

    async onDateChange(ev) {
        this.state.date = ev.target.value;
        return await this.loadAthletes();
    }

    toggleStatus(athlete) {
        const statuses = ['present', 'absent', 'excused'];
        const currentIndex = statuses.indexOf(athlete.status);
        const nextIndex = (currentIndex + 1) % statuses.length;
        athlete.status = statuses[nextIndex];
    }

    async saveAttendance() {
        try {
            const lines = this.state.athletes.map(a => ({
                athlete_id: a.id,
                status: a.status
            }));

            await this.orm.call("podium.attendance", "api_save_attendance", [], {
                date: this.state.date,
                category_id: this.state.selectedCategoryId ? parseInt(this.state.selectedCategoryId) : false,
                lines: lines
            });

            this.notification.add("Asistencia Guardada Correctamente", { type: "success" });
        } catch (error) {
            console.error(error);
            this.notification.add("Error al guardar asistencia", { type: "danger" });
        }
    }
}

registry.category("actions").add("ag_podium_base.attendance_kiosk", AttendanceKiosk);
