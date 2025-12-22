# Part of Avícola Management. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class AvicolaMortalidad(models.Model):
    _name = 'avicola.mortalidad'
    _description = 'Registro de Mortalidad'
    _order = 'fecha desc, id desc'

    lote_id = fields.Many2one('avicola.lote', string='Lote', required=True, ondelete='cascade')
    galpon_id = fields.Many2one(related='lote_id.galpon_id', string='Galpón', store=True)
    
    fecha = fields.Datetime(string='Fecha/Hora', required=True, default=fields.Datetime.now)
    cantidad = fields.Integer(string='Cantidad', required=True, default=1)
    
    causa = fields.Selection([
        ('natural', 'Muerte Natural'),
        ('enfermedad', 'Enfermedad'),
        ('asfixia', 'Asfixia/Calor'),
        ('aplastamiento', 'Aplastamiento'),
        ('descarte', 'Descarte Sanitario'),
        ('depredador', 'Depredador'),
        ('otro', 'Otra Causa'),
    ], string='Causa', default='natural')
    
    causa_detalle = fields.Char(string='Detalle de Causa')
    
    registrado_por = fields.Many2one('res.users', string='Registrado por', 
                                      default=lambda self: self.env.user)
    
    notas = fields.Text(string='Observaciones')
    
    @api.model
    def registrar_rapido(self, lote_id, cantidad, causa='natural'):
        """Método para registro rápido desde el dashboard OWL"""
        return self.create({
            'lote_id': lote_id,
            'cantidad': cantidad,
            'causa': causa,
        })
