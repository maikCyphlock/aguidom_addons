from odoo import models, fields

class Appointment(models.Model):
    _name = 'mecatec.appointment'
    _description = 'Mecatec Appointment'

    date = fields.Datetime(string='Date', required=True)
    client_id = fields.Many2one('res.partner', string='Client', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    reason = fields.Text(string='Reason')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')
