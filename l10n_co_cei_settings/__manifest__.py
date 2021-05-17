# -*- coding: utf-8 -*-
{
    'name': "Configuraciones por defecto para Facturación electrónica Colombia",

    'summary': """
        Required fields for electronic invoicing generation.""",

    'description': """
        Adds default required fields to the invoice Odoo model, to allow
        electronic involicing, and creates some tabs for company and partner 
        settings. This is a l10n_co_cei auxiliary module.
    """,

    'author': "Pragmatic S.A.S.",
    'website': "https://www.pragmatic.com.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Invoicing & Payments',
    'version': '13.3.8.3',
    'license': 'OPL-1',
    'support': 'soporte.fe@pragmatic.com.co',
    'images': ['static/description/icon.jpg'],

    # any module necessary for this one to work correctly
    'depends': ['base', 'account','l10n_co', 'contacts', 'mail', 'l10n_co_cei_fe','l10n_co_postal'],

    # always loaded
    'data': [
        # security
        'security/ir.model.access.csv',
        'views/responsabilidad_fiscal_view.xml',
        'data/responsabilidad_fiscal.xml',
        'views/res_partner.xml',
        'views/fiscal_responsibility_config.xml',
    ],
}
