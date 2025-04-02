from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Position(models.Model):
    _name = 'security.assets.position'
    _description = 'Position'
    _rec_name = 'display_name'
    _inherit = ['mail.thread']

    facility_id = fields.Many2one(
        'security.assets.facility',
        string='Puesto',
        ondelete='cascade',
        required=True,
        tracking=True
    )

    display_name = fields.Char(compute="_compute_display_name", store=True)
    description = fields.Char(string='Ubicacion', required=True)
    weapon_id = fields.Many2one(
        'security.assets.weapon',
        string='Arma Asignada',
        ondelete='restrict',
        domain="[('position_id', '=', False), ('warehouse_id', '=', False)]",
        tracking=True
    )
    notes = fields.Text(string='Notas Adicionales', tracking=True)

    _sql_constraints = [
        ('unique_position_weapon', 'UNIQUE(weapon_id)', 'Cada ubicación solo puede tener un arma asignada'),
        ('unique_position', 'UNIQUE(facility_id, description)', 'Esta ubicacion ya existe para este puesto.')
    ]

    @api.depends('facility_id', 'description')
    def _compute_display_name(self):
        for record in self:
            if record.id:
                record.display_name = f"{record.facility_id.partner_id.name} - {record.facility_id.location_name} - {record.description}"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('description') and vals['description']:
                vals['description'] = vals['description'].title()
            record = super(Position, self).create(vals)
            if record.weapon_id:
                record.weapon_id._log_weapon_movement('assigned', record)
                record.weapon_id.position_id = record
            return record

    def write(self, vals):
        if vals.get('description') and vals['description']:
            vals['description'] = vals['description'].title()
        for record in self:
            previous_weapon = record.weapon_id
            if 'weapon_id' in vals and not vals.get('weapon_id'):
                if previous_weapon:
                    previous_weapon._log_weapon_movement('unassigned', record)
                    previous_weapon.position_id = False
        res = super(Position, self).write(vals)
        for record in self:
            new_weapon = record.weapon_id
            if 'weapon_id' in vals:
                if new_weapon and previous_weapon != new_weapon:
                    new_weapon.position_id = record
                    new_weapon._log_weapon_movement('assigned', record)
        return res

    @api.constrains('weapon_id')
    def _check_unique_weapon(self):
        for record in self:
            if record.weapon_id and record.weapon_id.position_id and record.weapon_id.position_id != record:
                raise ValidationError("Este arma ya está asignada a otra ubicación.")