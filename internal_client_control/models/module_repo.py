from odoo import models, fields

class TelemetryModuleRepo(models.Model):
    _name = 'telemetry.module.repo'
    _description = 'Module GitHub Repository Configuration'
    _order = 'name'

    name = fields.Char(string='Module Name', required=True, index=True, help="Technical name of the module (e.g. 'mecatec')")
    github_repo = fields.Char(string='GitHub Repository', required=True, help="Format: owner/repo (e.g. 'odookistan/mecatec')")
    github_branch = fields.Char(string='GitHub Branch', default='18.0', required=True)
    
    last_checked = fields.Datetime(string='Last Checked')
    latest_commit_hash = fields.Char(string='Latest Commit Hash')
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Module name must be unique!')
    ]
