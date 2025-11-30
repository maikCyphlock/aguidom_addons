from odoo import models, fields

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    # Standard fields: brand_id (brand), model_id (model), model_year (year), license_plate, vin_sn (vin)
    
    # Fleet vehicles usually belong to the company (driver_id). 
    # We add owner_id to explicitly link to an external client.
    owner_id = fields.Many2one('res.partner', string='Owner')
