# -*- coding: utf-8 -*-
{
    'name': "Real Estate",
    'summary': "Manage Properties and Real Estate Offers",
    'description': """
        Modul Enterprise Real Estate:
        - Manajemen Properti & Penawaran
        - Wizard Popup Penawaran Interaktif
        - Role & Record Rules (Agent vs Manager)
        - QWeb PDF Reporting & Mail Tracking
    """,
    'author': "Developer",
    'category': 'Real Estate',
    'version': '17.0.1.0.0',
    'depends': ['base', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizards/property_offer_wizard_views.xml',
        'views/views.xml',
        'reports/property_report.xml',
        'data/demo_data.xml',
    ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
