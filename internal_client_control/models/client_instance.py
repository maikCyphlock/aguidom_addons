from odoo import models, fields, api

class ClientInstance(models.Model):
    _name = "client.instance"
    _description = "Cliente de control de versiones"

    name = fields.Char("nombre del cliente", required=True)
    last_report = fields.Datetime("ultima fecha de reporte", readonly=True)
    module_ids = fields.One2many("client.module.status", 'instance_id', string="Modulos")
    