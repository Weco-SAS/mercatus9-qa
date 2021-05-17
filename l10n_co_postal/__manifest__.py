# -*- coding: utf-8 -*-
{
    'name': "Configuración Codigo Postales DIAN Colombia",

    'summary': """
        Crea un modelo para gestión de codigos postales. Adiciona un modelo con el paquete de codigos postales""",

    'description': """
        Crea un modelo para gestión de codigos postales. Adiciona un modelo con el paquete de codigos postales.
        crea un menu en las configuraciones para la asignacion de codigos postales.
    """,

    'author': "Pragmatic SAS",
    'website': "http://www.pragmatic.com.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Invoicing & Payments',
    'version': '13.3.8.3',
    'license': 'OPL-1',
    'support': 'soporte@pragmatic.com.co',
    'images': ['static/description/icon.jpg'],

    # any module necessary for this one to work correctly
    'depends': ['base','base_setup'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/config_fe_details.xml',
        'data/config_fe.xml',
        'views/postal_view.xml',
        'views/postal_config.xml',
        'views/res_partner.xml',
        'views/config_fe.xml'
    ],
}
