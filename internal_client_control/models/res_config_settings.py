from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    github_api_token = fields.Char(string='GitHub API Token', config_parameter='internal_client_control.github_api_token', help="Token for accessing private repositories")
