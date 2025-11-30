from odoo import models, fields, api

class PodiumAthlete(models.Model):
    _name = 'podium.athlete'
    _description = 'Atleta'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', string='Contacto Relacionado', required=True, ondelete='cascade')
    birth_date = fields.Date(string='Fecha de Nacimiento')
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro')
    ], string='Género')
    height = fields.Float(string='Altura (m)')
    weight = fields.Float(string='Peso (kg)')
    age = fields.Integer(string='Edad', compute='_compute_age')
    representative_id = fields.Many2one('res.partner', string='Representante', domain=[('is_podium_representative', '=', True)])
    category_id = fields.Many2one('podium.category', string='Categoría', compute='_compute_category')
    
    club_id = fields.Many2one('podium.club', related='partner_id.club_id', store=True, string='Club', readonly=False)

    payment_ids = fields.One2many('podium.payment', 'athlete_id', string='Pagos')
    attendance_line_ids = fields.One2many('podium.attendance.line', 'athlete_id', string='Asistencias')
    
    image_128 = fields.Image(string="Imagen", compute='_compute_image', store=True)
    active = fields.Boolean(default=True, string='Activo')

    @api.depends('partner_id.image_128')
    def _compute_image(self):
        for record in self:
            record.image_128 = record.partner_id.image_128

    def _compute_age(self):
        for athlete in self:
            if athlete.birth_date:
                athlete.age = (fields.Date.today() - athlete.birth_date).days // 365
            else:
                athlete.age = 0
    def _compute_category(self):
        for athlete in self:
            if athlete.age:
                athlete.category_id = self.env['podium.category'].search([('age_min', '<=', athlete.age), ('age_max', '>=', athlete.age)], limit=1)
            else:
                athlete.category_id = False
    @api.model
    def create(self, vals):
        if 'partner_id' not in vals:
            # If creating athlete without existing partner, ensure flags are set on the new partner created by inheritance
            # Actually, _inherits handles creation, but we might want to force flags if we could intercept the partner creation.
            # However, with _inherits, we pass vals to create.
            vals['is_podium_athlete'] = True
        else:
             # If linking to existing partner, update it
             self.env['res.partner'].browse(vals['partner_id']).write({'is_podium_athlete': True})
        
        return super(PodiumAthlete, self).create(vals)