from odoo import models, fields

class Partner(models.Model):
    _inherit = 'res.partner'

    cedula = fields.Char(string='Cédula (ID)')
    is_mecatec_client = fields.Boolean(string='Is Mecatec Client')
