# -*- coding: utf-8 -*-

{
    'name': 'Mercado Pago Payment Acquirer for Colombia',
    'category': 'Accounting',
    'summary': 'Mercado Pago Implementation for Odoo eCommerce version 13.0 / Colombia',
    'version': '13.1.27.0',
    'description': """Mercado Pago Payment Acquirer Colombia""",
    'author': 'Moldeo Interactive',
    'website': 'https://www.moldeointeractive.com',
    'depends': ['payment','website','website_sale'],
    'data': [
        'views/mercadopago.xml',
        'views/payment_acquirer.xml',
        #'views/res_config_view.xml',
        'data/mercadopago.xml',
    ],
    'price': '50.00',
    'currency': 'USD',
    'images': ['src/img/mercadopago_icon.png','src/img/mercadopago_logo.png',
                'src/img/mercadopago_logo_64.png',
                'static/description/payment_mercadopago_screenshot.png','static/description/main_screenshot.png',
                'static/description/main2_screenshot.png',
                'static/description/create_application_mp_sreenshot.png','static/description/credentials_mercadopago_screenshot.png'],
    'installable': True,
    'license': 'GPL-3',
    'post_init_hook': 'create_missing_journal_for_acquirers',
}
