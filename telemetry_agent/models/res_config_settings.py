from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    telemetry_client_name = fields.Char(config_parameter='telemetry.client_name', string="Client Name")
    telemetry_hq_url = fields.Char(config_parameter='telemetry.hq_url', string="Telemetry HQ URL")
