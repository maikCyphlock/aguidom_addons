from odoo import models, fields, api
from datetime import date

class PodiumPayment(models.Model):
    _name = 'podium.payment'
    _description = 'Mensualidad'
    _order = 'date desc, id desc'
    
    name = fields.Char(string='Referencia', compute='_compute_name', store=True)

    athlete_id = fields.Many2one('podium.athlete', string='Atleta', required=True)
    club_id = fields.Many2one('podium.club', related='athlete_id.club_id', store=True, string='Club', readonly=True)
    
    @api.depends('athlete_id', 'month', 'year')
    def _compute_name(self):
        for record in self:
            record.name = f"Pago {record.month}/{record.year} - {record.athlete_id.name or ''}"

    date = fields.Date(string='Fecha de Pago', default=fields.Date.context_today, required=True)
    amount = fields.Monetary(string='Monto', currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', string='Moneda', default=lambda self: self.env.company.currency_id)
    
    month = fields.Selection([
        ('01', 'Enero'), ('02', 'Febrero'), ('03', 'Marzo'),
        ('04', 'Abril'), ('05', 'Mayo'), ('06', 'Junio'),
        ('07', 'Julio'), ('08', 'Agosto'), ('09', 'Septiembre'),
        ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
    ], string='Mes Correspondiente', required=True)
    
    year = fields.Integer(string='Año', default=lambda self: date.today().year, required=True)
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('paid', 'Pagado')
    ], string='Estado', default='draft', required=True)
    
    bcv_rate = fields.Float(string='Tasa BCV', digits=(12, 4), help="Tasa de cambio del Banco Central de Venezuela para el día del pago.")
    payment_proof = fields.Binary(string='Comprobante de Pago', attachment=True)
    payment_proof_filename = fields.Char(string='Nombre del Archivo')
    
    notes = fields.Text(string='Notas')

    def action_confirm(self):
        self.write({'state': 'paid'})

    def action_draft(self):
        self.write({'state': 'draft'})
