# -*- coding: utf-8 -*-
import logging
import validators

from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = "res.partner"

    vat = fields.Char(string='Identification Number', help="Identification Number for selected type")
    webchat = fields.Char(string='Webchat', default='')
    fe_tipo_documento = fields.Selection(
        selection=[
                    ('11', 'Registro civil'),
                    ('12', 'Tarjeta de identidad'),
                    ('13', 'Cédula de ciudadanía'),
                    ('21', 'Tarjeta de extranjería'),
                    ('22', 'Cédula de extranjería'),
                    ('31', 'NIT'),
                    ('41', 'Pasaporte'),
                    ('42', 'Documento de identificación extranjero'),
                    ('50', 'NIT de otro país'),
                    ('91', 'NUIP'),
                 ],
        string='Tipo de documento',
        default="22"
    )