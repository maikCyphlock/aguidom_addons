# Part of Avícola Management. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class AvicolaAlimento(models.Model):
    _name = 'avicola.alimento'
    _description = 'Inventario de Alimento'
    _order = 'tipo, name'

    name = fields.Char(string='Nombre', required=True)
    
    tipo = fields.Selection([
        ('iniciador', 'Iniciador (0-10 días)'),
        ('crecimiento', 'Crecimiento (11-24 días)'),
        ('engorde', 'Engorde (25+ días)'),
        ('ponedora', 'Ponedoras'),
        ('reproductora', 'Reproductoras'),
    ], string='Tipo', required=True)
    
    marca = fields.Char(string='Marca/Proveedor')
    
    # Stock
    stock_kg = fields.Float(string='Stock (kg)', digits=(12, 2), required=True)
    stock_minimo = fields.Float(string='Stock Mínimo (kg)', digits=(12, 2), default=100)
    stock_maximo = fields.Float(string='Stock Máximo (kg)', digits=(12, 2))
    
    # Precio
    precio_kg = fields.Float(string='Precio por kg', digits=(12, 2))
    valor_inventario = fields.Float(string='Valor Inventario', compute='_compute_valor')
    
    # Estado
    estado = fields.Selection([
        ('normal', 'Normal'),
        ('bajo', 'Stock Bajo'),
        ('critico', 'Crítico'),
        ('agotado', 'Agotado'),
    ], string='Estado', compute='_compute_estado', store=True)
    
    active = fields.Boolean(default=True)
    notas = fields.Text(string='Notas')
    
    # Consumo proyectado
    consumo_diario_promedio = fields.Float(string='Consumo Diario Promedio (kg)', digits=(12, 2))
    dias_stock_restante = fields.Float(string='Días de Stock', compute='_compute_dias_stock')
    
    @api.depends('stock_kg', 'precio_kg')
    def _compute_valor(self):
        for alimento in self:
            alimento.valor_inventario = alimento.stock_kg * alimento.precio_kg
    
    @api.depends('stock_kg', 'stock_minimo')
    def _compute_estado(self):
        for alimento in self:
            if alimento.stock_kg <= 0:
                alimento.estado = 'agotado'
            elif alimento.stock_kg < alimento.stock_minimo * 0.5:
                alimento.estado = 'critico'
            elif alimento.stock_kg < alimento.stock_minimo:
                alimento.estado = 'bajo'
            else:
                alimento.estado = 'normal'
    
    @api.depends('stock_kg', 'consumo_diario_promedio')
    def _compute_dias_stock(self):
        for alimento in self:
            if alimento.consumo_diario_promedio > 0:
                alimento.dias_stock_restante = alimento.stock_kg / alimento.consumo_diario_promedio
            else:
                alimento.dias_stock_restante = 0
    
    def action_ajustar_stock(self, cantidad, tipo='entrada'):
        """Ajuste de stock desde dashboard"""
        for alimento in self:
            if tipo == 'entrada':
                alimento.stock_kg += cantidad
            else:
                alimento.stock_kg = max(0, alimento.stock_kg - cantidad)
