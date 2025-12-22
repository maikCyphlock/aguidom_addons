# Part of Avícola Management. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class AvicolaGalpon(models.Model):
    _name = 'avicola.galpon'
    _description = 'Galpón Avícola'
    _order = 'sequence, name'

    name = fields.Char(string='Nombre', required=True)
    sequence = fields.Integer(default=10)
    capacidad = fields.Integer(string='Capacidad (aves)', required=True)
    ubicacion = fields.Char(string='Ubicación')
    
    # Sensores y estado actual
    temperatura_actual = fields.Float(string='Temperatura (°C)', digits=(4, 1))
    humedad_actual = fields.Float(string='Humedad (%)', digits=(4, 1))
    temperatura_minima = fields.Float(string='Temp. Mínima Alerta', default=25.0)
    temperatura_maxima = fields.Float(string='Temp. Máxima Alerta', default=32.0)
    
    estado_sanitario = fields.Selection([
        ('optimo', 'Óptimo'),
        ('alerta', 'En Alerta'),
        ('critico', 'Crítico'),
    ], string='Estado Sanitario', default='optimo', compute='_compute_estado', store=True)
    
    # Relaciones
    lote_ids = fields.One2many('avicola.lote', 'galpon_id', string='Lotes')
    lote_activo_id = fields.Many2one('avicola.lote', string='Lote Activo', 
                                      compute='_compute_lote_activo', store=True)
    
    # Estadísticas computadas
    aves_actuales = fields.Integer(string='Aves Actuales', compute='_compute_estadisticas')
    porcentaje_ocupacion = fields.Float(string='% Ocupación', compute='_compute_estadisticas')
    mortalidad_acumulada = fields.Float(string='% Mortalidad', compute='_compute_estadisticas')
    
    active = fields.Boolean(default=True)
    notas = fields.Text(string='Notas')
    
    @api.depends('lote_ids.state')
    def _compute_lote_activo(self):
        for galpon in self:
            lote = galpon.lote_ids.filtered(lambda l: l.state == 'activo')[:1]
            galpon.lote_activo_id = lote.id if lote else False
    
    @api.depends('lote_activo_id', 'lote_activo_id.cantidad_actual', 
                 'lote_activo_id.cantidad_inicial', 'capacidad')
    def _compute_estadisticas(self):
        for galpon in self:
            lote = galpon.lote_activo_id
            if lote and lote.cantidad_inicial > 0:
                galpon.aves_actuales = lote.cantidad_actual
                galpon.porcentaje_ocupacion = (lote.cantidad_actual / galpon.capacidad) * 100 if galpon.capacidad else 0
                muertes = lote.cantidad_inicial - lote.cantidad_actual
                galpon.mortalidad_acumulada = (muertes / lote.cantidad_inicial) * 100
            else:
                galpon.aves_actuales = 0
                galpon.porcentaje_ocupacion = 0
                galpon.mortalidad_acumulada = 0
    
    @api.depends('temperatura_actual', 'temperatura_minima', 'temperatura_maxima', 
                 'mortalidad_acumulada')
    def _compute_estado(self):
        for galpon in self:
            if galpon.mortalidad_acumulada > 5:
                galpon.estado_sanitario = 'critico'
            elif (galpon.temperatura_actual and 
                  (galpon.temperatura_actual < galpon.temperatura_minima or 
                   galpon.temperatura_actual > galpon.temperatura_maxima)):
                galpon.estado_sanitario = 'alerta'
            elif galpon.mortalidad_acumulada > 2:
                galpon.estado_sanitario = 'alerta'
            else:
                galpon.estado_sanitario = 'optimo'
