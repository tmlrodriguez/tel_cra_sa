# -*- coding: utf-8 -*-
{
    'name': 'Activos de Seguridad',
    'summary': 'Gestiona activos tácticos entre posiciones y ubicaciones',
    'description': 'Gestión y manejo de activos de seguridad',
    'author': 'Telematica',
    'category': 'Base',
    'version': '18.0.0.1',
    'depends': ['base', 'mail', 'hr'],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Reports
        'reports/all_weapons_report.xml',
        'reports/all_weapons_report_template.xml',
        'reports/position_weapons_report.xml',
        'reports/position_weapons_report_template.xml',
        'reports/weapon_assignment_report.xml',
        'reports/weapon_assignment_report_template.xml',
        # Views
        'views/security_assets_employee_view.xml',
        'views/security_assets_facility_view.xml',
        'views/security_assets_position_view.xml',
        'views/security_assets_weapon_view.xml',
        # Menu
        'views/security_assets_menu.xml',
    ],
    'assets': {
            'web.assets_backend': [
                'security_assets/static/img/icon.png',
            ],
    },
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
