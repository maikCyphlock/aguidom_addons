from odoo import fields, models, api

class ModuleStatus(models.Model):
    _name = "client.module.status"
    _description = "Estado del modulo"

    instance_id = fields.Many2one("client.instance", string="Instancia", required=True, ondelete='cascade')
    module_name = fields.Char(string="Nombre del Modulo", required=True)
    
    # Version tracking
    manifest_version = fields.Char(string='Versión Manifest')
    content_hash = fields.Char(string='Hash Contenido')
    git_branch = fields.Char(string='Rama Git')
    git_commit = fields.Char(string='Commit Git')
    
    state = fields.Selection([
        ('latest', 'Latest'),
        ('outdated', 'Outdated'),
        ('manual', 'Manual Change'),
        ('untracked', 'Untracked')
    ], string='Status', default='untracked', help="Comparison with GitHub")