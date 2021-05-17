# -*- coding: utf-8 -*-
{
    'name': "Personalización de Odoo para Abacus",

    'summary': """
        Personalización de Odoo para Abacus""",

    'description': """
        Genera la descripción de los items de la factura en un idioma específico definido en el cliente 
    """,

    'author': "Pragmatic SAS",
    'website': "http://www.pragmatic.com.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv'
        'views/templates.xml',
        'views/res_partner.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
