# Part of Avícola Management. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class AvicolaRecoleccion(models.Model):
    _name = 'avicola.recoleccion'
    _description = 'Recolección de Huevos'
    _order = 'fecha desc, id desc'

    lote_id = fields.Many2one('avicola.lote', string='Lote', required=True, 
                               domain=[('tipo_produccion', '=', 'ponedora')],
                               ondelete='cascade')
    galpon_id = fields.Many2one(related='lote_id.galpon_id', string='Galpón', store=True)
    
    fecha = fields.Datetime(string='Fecha/Hora', required=True, default=fields.Datetime.now)
    cantidad = fields.Integer(string='Cantidad Huevos', required=True)
    
    clasificacion = fields.Selection([
        ('jumbo', 'Jumbo (>73g)'),
        ('extra_grande', 'Extra Grande (63-73g)'),
        ('grande', 'Grande (53-63g)'),
        ('mediano', 'Mediano (44-53g)'),
        ('pequeno', 'Pequeño (<44g)'),
        ('roto', 'Rotos/Descarte'),
    ], string='Clasificación', default='grande')
    
    # Estadísticas
    huevos_rotos = fields.Integer(string='Huevos Rotos', default=0)
    huevos_sucios = fields.Integer(string='Huevos Sucios', default=0)
    
    registrado_por = fields.Many2one('res.users', string='Registrado por',
                                      default=lambda self: self.env.user)
    
    notas = fields.Text(string='Observaciones')
    
    @api.model
    def registrar_rapido(self, lote_id, cantidad, clasificacion='grande'):
        """Método para registro rápido desde el dashboard OWL"""
        return self.create({
            'lote_id': lote_id,
            'cantidad': cantidad,
            'clasificacion': clasificacion,
        })
