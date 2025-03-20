from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    district_supervisor_id = fields.Many2one(
        'hr.employee',
        string="Jefe de Distrito",
        domain="[('job_id.name', '=', 'Jefe de Distrito')]",
        tracking=True
    )

    supervisor_ids = fields.One2many(
        'hr.employee',
        'district_supervisor_id',
        string='Supervisores',
        domain="[('job_id.name', '=', 'Supervisor'), ('district_supervisor_id', '=', False)]",
        tracking=True
    )

    facility_ids = fields.Many2many(
        'security.assets.facility',
        'facility_supervisor_rel',
        'supervisor_id',
        'facility_id',
        string='Facilities',
        tracking=True
    )

    selected_job_name = fields.Char(string="Hide District Supervisor", compute="_compute_selected_job_name", store=False)

    @api.onchange('job_id')
    def _compute_selected_job_name(self):
        for record in self:
            record.selected_job_name = record.job_id.name if record.job_id else ""

    @api.onchange('job_id')
    def _remove_district_supervisor_id(self):
        for record in self:
            record.district_supervisor_id = False
            record.facility_ids = False

    @api.constrains('job_id', 'district_supervisor_id')
    def _check_validations(self):
        for record in self:
            if not record.job_id:
                raise ValidationError("El campo 'Puesto' no puede estar vacío.")

            if record.job_id.name == 'Supervisor' and not record.district_supervisor_id:
                raise ValidationError("Un Supervisor debe tener asignado un Jefe de Distrito.")