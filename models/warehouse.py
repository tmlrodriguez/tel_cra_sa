from odoo import models, fields, api

class Warehouse(models.Model):
    _name = 'security.assets.warehouse'
    _description = 'Almacén de Armas'
    _rec_name = 'name'
    _inherit = ['mail.thread']

    name = fields.Char(string='Nombre del Almacén', required=True, tracking=True)
    address = fields.Text(string='Dirección', required=True, tracking=True)
    notes = fields.Text(string='Notas Adicionales', required=False, tracking=True)
    weapon_ids = fields.One2many(
        'security.assets.weapon',
        'warehouse_id',
        string='Armas Almacenadas',
        domain="[('warehouse_id', '=', False), ('position_id', '=', False)]",)

    @api.model_create_multi
    def create(self, vals_list):
        records = super(Warehouse, self).create(vals_list)
        for record, vals in zip(records, vals_list):
            if vals.get('name'):
                record.name = vals['name'].title()
            if vals.get('address'):
                record.address = vals['address'].title()
            weapon_ids = vals.get('weapon_ids', [])
            for command in weapon_ids:
                if command[0] == 4:
                    weapon = self.env['security.assets.weapon'].browse(command[1])
                    weapon._log_weapon_movement('stored', warehouse=record)
                else:
                    for weapon_id in command[2]:
                        weapon = self.env['security.assets.weapon'].browse(weapon_id)
                        weapon._log_weapon_movement('removed', warehouse=record)
        return records

    def write(self, vals):
        if vals.get('name'):
            vals['name'] = vals['name'].title()
        if vals.get('address'):
            vals['address'] = vals['address'].title()
        prev_weapons = {rec.id: set(rec.weapon_ids.ids) for rec in self}
        res = super().write(vals)
        for record in self:
            new_weapons = set(record.weapon_ids.ids)
            old_weapons = prev_weapons.get(record.id, set())
            added = new_weapons - old_weapons
            removed = old_weapons - new_weapons
            for weapon in self.env['security.assets.weapon'].browse(added):
                weapon._log_weapon_movement('stored', warehouse=record)
            for weapon in self.env['security.assets.weapon'].browse(removed):
                weapon._log_weapon_movement('removed', warehouse=record)
        return res



