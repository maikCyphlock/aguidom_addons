from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # We can add specific Mecatec fields here if needed.
    # For now, we rely on standard fields: name, list_price (price), qty_available (quantity), default_code (serial/ref)
    pass
