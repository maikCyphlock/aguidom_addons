from odoo import models, fields

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    # Standard fields: name (title), description, request_date (date), stage_id (status), user_id (mechanic)
    
    # Add missing relations
    client_id = fields.Many2one('res.partner', string='Client')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
