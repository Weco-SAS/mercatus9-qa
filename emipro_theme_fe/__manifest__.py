# -*- coding: utf-8 -*-
{
    # Theme information
    'name': 'Emipro Theme F.E',
    'category': 'Base',
    'summary': 'Integracion para factura electonica.',
    'version': '1.0.0',
    'license': 'OPL-1',
    'depends': [
                    'base', 'l10n_co_cei_settings'
                ],

    'data': [
                'views/res_partner.xml',
                'templates/website.xml'
            ],

    #Odoo Store Specific
    'images': [
                'static/description/emipro_theme_base.jpg',
              ],

    # Author
    'author': 'WECO.co',
    'website': '',
    'maintainer': 'WECO',

    # Technical
    'installable': True,
    'auto_install': False,
}
