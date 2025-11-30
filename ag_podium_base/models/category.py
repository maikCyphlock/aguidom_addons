from odoo import models, fields

class PodiumCategory(models.Model):
    _name = 'podium.category'
    _description = 'Categoría de Atleta'

    name = fields.Char(string='Nombre', required=True)
    age_min = fields.Integer(string='Edad Mínima')
    age_max = fields.Integer(string='Edad Máxima')
    description = fields.Text(string='Descripción')
