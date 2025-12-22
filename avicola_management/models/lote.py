# Part of Avícola Management. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from datetime import date, timedelta


class AvicolaLote(models.Model):
    _name = 'avicola.lote'
    _description = 'Lote de Aves'
    _order = 'fecha_ingreso desc'
    _rec_name = 'display_name'

    name = fields.Char(string='Código Lote', required=True, copy=False)
    display_name = fields.Char(compute='_compute_display_name', store=True)
    
    galpon_id = fields.Many2one('avicola.galpon', string='Galpón', required=True, ondelete='restrict')
    
    # Información del lote
    raza = fields.Selection([
        ('ross_308', 'Ross 308'),
        ('ross_708', 'Ross 708'),
        ('cobb_500', 'Cobb 500'),
        ('cobb_700', 'Cobb 700'),
        ('hubbard', 'Hubbard'),
        ('hy_line', 'Hy-Line (Ponedoras)'),
        ('lohmann', 'Lohmann (Ponedoras)'),
        ('otro', 'Otra'),
    ], string='Raza', required=True, default='ross_308')
    
    tipo_produccion = fields.Selection([
        ('engorde', 'Pollos de Engorde'),
        ('ponedora', 'Gallinas Ponedoras'),
        ('reproductora', 'Reproductoras'),
    ], string='Tipo de Producción', required=True, default='engorde')
    
    # Fechas
    fecha_ingreso = fields.Date(string='Fecha de Ingreso', required=True, default=fields.Date.today)
    fecha_salida_proyectada = fields.Date(string='Fecha Salida Proyectada', compute='_compute_fechas')
    fecha_salida_real = fields.Date(string='Fecha Salida Real')
    
    # Cantidades
    cantidad_inicial = fields.Integer(string='Aves Iniciales', required=True)
    cantidad_actual = fields.Integer(string='Aves Actuales', compute='_compute_cantidad_actual', store=True)
    
    # Pesos
    peso_inicial_promedio = fields.Float(string='Peso Inicial Promedio (g)', digits=(8, 2))
    peso_actual_promedio = fields.Float(string='Peso Actual Promedio (g)', digits=(8, 2))
    peso_objetivo = fields.Float(string='Peso Objetivo (g)', digits=(8, 2))
    
    # Estado
    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('activo', 'Activo'),
        ('vendido', 'Vendido'),
        ('descartado', 'Descartado'),
    ], string='Estado', default='borrador')
    
    # Computados
    edad_dias = fields.Integer(string='Edad (días)', compute='_compute_edad')
    dias_para_salida = fields.Integer(string='Días para Salida', compute='_compute_fechas')
    progreso_ciclo = fields.Float(string='Progreso Ciclo (%)', compute='_compute_fechas')
    
    # Relaciones
    mortalidad_ids = fields.One2many('avicola.mortalidad', 'lote_id', string='Registros Mortalidad')
    recoleccion_ids = fields.One2many('avicola.recoleccion', 'lote_id', string='Recolecciones')
    
    # Estadísticas
    total_mortalidad = fields.Integer(string='Total Mortalidad', compute='_compute_estadisticas')
    porcentaje_mortalidad = fields.Float(string='% Mortalidad', compute='_compute_estadisticas')
    total_huevos = fields.Integer(string='Total Huevos', compute='_compute_estadisticas')
    
    notas = fields.Text(string='Notas')
    
    @api.depends('name', 'galpon_id.name', 'edad_dias')
    def _compute_display_name(self):
        for lote in self:
            galpon = lote.galpon_id.name or ''
            lote.display_name = f"{lote.name} - {galpon} ({lote.edad_dias}d)"
    
    @api.depends('fecha_ingreso')
    def _compute_edad(self):
        today = date.today()
        for lote in self:
            if lote.fecha_ingreso:
                lote.edad_dias = (today - lote.fecha_ingreso).days
            else:
                lote.edad_dias = 0
    
    @api.depends('fecha_ingreso', 'tipo_produccion', 'edad_dias')
    def _compute_fechas(self):
        for lote in self:
            if lote.tipo_produccion == 'engorde':
                ciclo_dias = 42  # 6 semanas típico para engorde
            elif lote.tipo_produccion == 'ponedora':
                ciclo_dias = 540  # ~18 meses
            else:
                ciclo_dias = 365
            
            if lote.fecha_ingreso:
                lote.fecha_salida_proyectada = lote.fecha_ingreso + timedelta(days=ciclo_dias)
                lote.dias_para_salida = max(0, ciclo_dias - lote.edad_dias)
                lote.progreso_ciclo = min(100, (lote.edad_dias / ciclo_dias) * 100)
            else:
                lote.fecha_salida_proyectada = False
                lote.dias_para_salida = 0
                lote.progreso_ciclo = 0
    
    @api.depends('mortalidad_ids.cantidad', 'cantidad_inicial')
    def _compute_cantidad_actual(self):
        for lote in self:
            total_muertes = sum(lote.mortalidad_ids.mapped('cantidad'))
            lote.cantidad_actual = lote.cantidad_inicial - total_muertes
    
    @api.depends('mortalidad_ids.cantidad', 'recoleccion_ids.cantidad', 'cantidad_inicial')
    def _compute_estadisticas(self):
        for lote in self:
            lote.total_mortalidad = sum(lote.mortalidad_ids.mapped('cantidad'))
            lote.porcentaje_mortalidad = (
                (lote.total_mortalidad / lote.cantidad_inicial) * 100 
                if lote.cantidad_inicial else 0
            )
            lote.total_huevos = sum(lote.recoleccion_ids.mapped('cantidad'))
    
    def action_activar(self):
        self.write({'state': 'activo'})
    
    def action_vender(self):
        self.write({'state': 'vendido', 'fecha_salida_real': date.today()})
