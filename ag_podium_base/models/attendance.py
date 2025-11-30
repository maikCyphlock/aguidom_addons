from odoo import models, fields, api
from datetime import date

class PodiumAttendance(models.Model):
    _name = 'podium.attendance'
    _description = 'Hoja de Asistencia'
    _order = 'date desc, id desc'

    date = fields.Date(string='Fecha', default=fields.Date.context_today, required=True)
    category_id = fields.Many2one('podium.category', string='Categoría (Opcional)')
    club_id = fields.Many2one('podium.club', string='Club', required=True, default=lambda self: self.env.user.partner_id.club_id)
    line_ids = fields.One2many('podium.attendance.line', 'attendance_id', string='Asistencias')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado')
    ], string='Estado', default='draft', required=True)
    
    name = fields.Char(string='Referencia', compute='_compute_name', store=True)

    @api.depends('date', 'category_id')
    def _compute_name(self):
        for record in self:
            cat_name = record.category_id.name if record.category_id else 'General'
            record.name = f"Asistencia {record.date} - {cat_name}"

    def action_generate_lines(self):
        self.ensure_one()
        # Clear existing lines to avoid duplicates if clicked twice (or handle updates smartly)
        # For simplicity, we'll just add missing athletes or all if empty.
        # Let's go with: Find active athletes matching category.
        
        domain = [('active', '=', True)]
        if self.category_id:
            domain.append(('category_id', '=', self.category_id.id))
            
        athletes = self.env['podium.athlete'].search(domain)
        
        existing_athlete_ids = self.line_ids.mapped('athlete_id.id')
        
        lines_to_create = []
        for athlete in athletes:
            if athlete.id not in existing_athlete_ids:
                lines_to_create.append({
                    'attendance_id': self.id,
                    'athlete_id': athlete.id,
                    'status': 'present',
                })
        
        if lines_to_create:
            self.env['podium.attendance.line'].create(lines_to_create)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_draft(self):
        self.write({'state': 'draft'})

    @api.model
    def api_save_attendance(self, date, category_id, lines):
        """
        API method called from Owl Kiosk to save attendance.
        :param date: String 'YYYY-MM-DD'
        :param category_id: Integer or False
        :param lines: List of dicts [{'athlete_id': int, 'status': str}]
        """
        # 1. Find or Create Attendance Record
        domain = [('date', '=', date)]
        if category_id:
            domain.append(('category_id', '=', category_id))
        else:
            domain.append(('category_id', '=', False))
            
        attendance = self.env['podium.attendance'].search(domain, limit=1)
        if not attendance:
            attendance = self.env['podium.attendance'].create({
                'date': date,
                'category_id': category_id or False,
                'state': 'confirmed'
            })
        
        # 2. Process Lines
        existing_lines = {line.athlete_id.id: line for line in attendance.line_ids}
        
        lines_to_create = []
        for line_data in lines:
            athlete_id = line_data['athlete_id']
            status = line_data['status']
            
            if athlete_id in existing_lines:
                if existing_lines[athlete_id].status != status:
                    existing_lines[athlete_id].write({'status': status})
            else:
                lines_to_create.append({
                    'attendance_id': attendance.id,
                    'athlete_id': athlete_id,
                    'status': status
                })
        
        if lines_to_create:
            self.env['podium.attendance.line'].create(lines_to_create)
            
        return True


class PodiumAttendanceLine(models.Model):
    _name = 'podium.attendance.line'
    _description = 'Línea de Asistencia'

    attendance_id = fields.Many2one('podium.attendance', string='Hoja de Asistencia', required=True, ondelete='cascade')
    athlete_id = fields.Many2one('podium.athlete', string='Atleta', required=True)
    status = fields.Selection([
        ('present', 'Presente'),
        ('absent', 'Ausente'),
        ('excused', 'Justificado')
    ], string='Estado', default='present', required=True)
    
    date = fields.Date(related='attendance_id.date', store=True, string='Fecha')


