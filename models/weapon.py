from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Model(models.Model):
    _name = 'security.assets.model'
    _description = 'Model'
    _rec_name = 'model'
    _inherit = ['mail.thread']

    brand_id = fields.Many2one('security.assets.brand', string='Marca', required=True, tracking=True)
    model = fields.Char(string='Modelo', unique=True, required=True, tracking=True)

    _sql_constraints = [
        ('unique_brand_model', 'UNIQUE(brand_id, model)', 'Este modelo ya existe.')
    ]

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.brand_id.brand} - {record.model}" if record.brand_id else record.model
            result.append((record.id, name))
        return result

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('model') and vals['model']:
                vals['model'] = vals['model'].title()
            return super(Model, self).create(vals)

    def write(self, vals):
        if vals.get('model') and vals['model']:
            vals['model'] = vals['model'].title()
        return super(Model, self).write(vals)


class Brand(models.Model):
    _name = 'security.assets.brand'
    _description = 'Brand'
    _rec_name = 'brand'
    _inherit = ['mail.thread']

    brand = fields.Char(string='Marca', unique=True, required=True, ondelete='restrict', tracking=True)
    model_ids = fields.One2many('security.assets.model', 'brand_id', string='Modelos', tracking=True)

    _sql_constraints = [
        ('unique_brand', 'UNIQUE(brand)', 'Esta marca ya existe.')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('brand') and vals['brand']:
                vals['brand'] = vals['brand'].title()
            return super(Brand, self).create(vals)

    def write(self, vals):
        if vals.get('brand') and vals['brand']:
            vals['brand'] = vals['brand'].title()
        return super(Brand, self).write(vals)


class Weapon(models.Model):
    _name = 'security.assets.weapon'
    _description = 'Weapon'
    _rec_name = 'display_name'
    _inherit = ['mail.thread']

    display_name = fields.Char(compute="_compute_display_name", store=True)
    brand_id = fields.Many2one('security.assets.brand', string='Marca', required=True, ondelete='restrict', tracking=True)
    model_id = fields.Many2one('security.assets.model', string='Modelo', required=True, ondelete='restrict', tracking=True)
    image = fields.Binary(string='Imagen del Arma', attachment=True)
    serial_number = fields.Char(string='No. de Serie', required=True, tracking=True)
    reference_number = fields.Char(string='No. de Referencia', required=True, tracking=True)
    weapon_status = fields.Selection([('new', 'Nueva'), ('poor', 'Mal Estado'), ('discarded', 'Descartada')], string='Estado del Arma', required=True, tracking=True)
    weapon_license = fields.Selection([('valid', 'Vigente'), ('expired', 'Vencidos'), ('no_document', 'Sin Papeles'), ('indistinct', 'Titular Distinto a Craes')], string='Permiso de Arma', required=True, tracking=True)
    valid_until = fields.Date(string='Vigente Hasta', tracking=True)
    position_id = fields.Many2one('security.assets.position', string='Ubicación Asignada', ondelete='restrict', domain="[('weapon_id', '=', False)]", readonly=True, tracking=True)
    notes = fields.Text(string='Notas Adicionales', tracking=True)
    history_ids = fields.One2many(
        'security.assets.weapon.history',
        'weapon_id',
        string="Historial de Movimientos",
        readonly=True
    )

    _sql_constraints = [
        ('unique_weapon', 'UNIQUE(brand_id, model_id, serial_number)', 'Esta arma con este modelo y numero de serie ya existe.'),
        ('unique_weapon_position', 'UNIQUE(position_id)', 'Cada arma solo puede estar asignada a una ubicación'),
        ('unique_reference_number', 'UNIQUE(reference_number)', 'Esta arma con este numero de referencia ya existe.'),
    ]

    @api.depends('brand_id', 'model_id', 'serial_number')
    def _compute_display_name(self):
        for record in self:
            if record.id:
                record.display_name = f"{record.brand_id.brand} - {record.model_id.model} ({record.serial_number})"

    @api.constrains('weapon_license', 'valid_until')
    def _check_valid_until(self):
        for record in self:
            if record.weapon_license == 'valid':
                if not record.valid_until:
                    raise ValidationError("Si el Permiso de Arma es 'Vigente', debe especificar una fecha en 'Vigente Hasta'.")
                valid_until_date = fields.Date.from_string(record.valid_until)
                if valid_until_date < fields.Date.today():
                    raise ValidationError("La fecha de expiración del permiso debe ser mayor a hoy.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('weapon_license') == 'valid':
                if not vals.get('valid_until'):
                    raise ValidationError("Si el Permiso de Arma es 'Vigente', debe especificar una fecha en 'Vigente Hasta'.")
                valid_until_date = fields.Date.from_string(vals.get('valid_until'))
                if valid_until_date < fields.Date.today():
                    raise ValidationError("La fecha de expiración del permiso debe ser mayor a hoy.")
            else:
                vals['valid_until'] = False
            return super().create(vals)

    def write(self, vals):
        for record in self:
            new_weapon_license = vals.get('weapon_license', record.weapon_license)
            new_valid_until = vals.get('valid_until', record.valid_until)
            if new_weapon_license == 'valid':
                if not new_valid_until:
                    raise ValidationError("Si el Permiso de Arma es 'Vigente', debe especificar una fecha en 'Vigente Hasta'.")
                valid_until_date = fields.Date.from_string(new_valid_until)
                if valid_until_date < fields.Date.today():
                    raise ValidationError("La fecha de expiración del permiso debe ser mayor a hoy.")
            else:
                vals['valid_until'] = False
        return super().write(vals)

    def _log_weapon_movement(self, movement_type, position):
        self.env['security.assets.weapon.history'].create({'weapon_id': self.id, 'position_id': position.id, 'movement_type': movement_type, 'movement_date': fields.Datetime.now()})

    def action_all_weapons_report(self):
        return self.env.ref('tel_cra_sa.action_all_weapons_report').report_action(self)

class WeaponMovementHistory(models.Model):
    _name = 'security.assets.weapon.history'
    _description = 'Historial de Movimientos de Armas'
    _order = 'movement_date desc'

    weapon_id = fields.Many2one('security.assets.weapon', string='Arma', required=True, ondelete='cascade')
    position_id = fields.Many2one('security.assets.position', string='Ubicación', ondelete='set null')
    movement_type = fields.Selection([
        ('assigned', 'Asignado'),
        ('unassigned', 'Desasignado')
    ], string="Tipo de Movimiento", required=True)
    movement_date = fields.Datetime(string="Fecha del Movimiento", default=fields.Datetime.now, required=True)


