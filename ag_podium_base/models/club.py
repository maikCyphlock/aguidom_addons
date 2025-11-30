from odoo import models, fields

class PodiumClub(models.Model):
    _name = 'podium.club'
    _description = 'Club Deportivo'

    name = fields.Char(string='Nombre del Club', required=True)
    code = fields.Char(string='Código', required=True)
    active = fields.Boolean(default=True, string='Activo')
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'El código del club debe ser único.')
    ]
