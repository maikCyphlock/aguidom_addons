from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    club_id = fields.Many2one('podium.club', string='Club Deportivo')
    
    is_podium_athlete = fields.Boolean(string='Es Atleta')
    is_podium_representative = fields.Boolean(string='Es Representante')
    is_podium_coach = fields.Boolean(string='Es Entrenador')
    is_podium_manager = fields.Boolean(string='Es Manager de Club')
