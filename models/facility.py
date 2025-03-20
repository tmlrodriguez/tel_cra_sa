from odoo import models, fields, api


class Facility(models.Model):
    _name = 'security.assets.facility'
    _description = 'Facility'
    _rec_name = 'display_name'
    _order = 'location_name'
    _inherit = ['mail.thread']

    display_name = fields.Char(compute='_compute_display_name', string='Display Name', store=True)
    partner_id = fields.Many2one('res.partner', string='Empresa', required=True, tracking=True)
    location_name = fields.Char(string='Nombre de Puesto', required=True, tracking=True)
    address = fields.Text(string='Dirección', required=True, tracking=True)
    notes = fields.Text(string="Notas Adicionales", tracking=True)

    position_ids = fields.One2many(
        'security.assets.position',
        'facility_id',
        string='Puestos'
    )

    supervisor_ids = fields.Many2many(
        'hr.employee',
        'facility_supervisor_rel',
        'facility_id',
        'supervisor_id',
        string='Supervisores',
        domain=[('job_id.name', '=', 'Supervisor')]
    )

    _sql_constraints = [
        ('unique_facility', 'UNIQUE(partner_id, location_name)', 'Este puesto ya existe.')
    ]

    @api.depends('partner_id', 'location_name')
    def _compute_display_name(self):
        for record in self:
            if record.id:
                record.display_name = f"{record.partner_id.name} - {record.location_name}"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('location_name') and vals['location_name']:
                vals['location_name'] = vals['location_name'].title()
        return super(Facility, self).create(vals_list)

    def write(self, vals):
        if vals.get('location_name') and vals['location_name']:
            vals['location_name'] = vals['location_name'].title()
        return super(Facility, self).write(vals)

