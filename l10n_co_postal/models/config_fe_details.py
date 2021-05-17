# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ConfigFEDetails(models.Model):
    _name = 'l10n_co_postal.config_cp_details'
    _description = "detalles de configuración para campos de códigos postales"

    name = fields.Char(string='Nombre del campo')
    description = fields.Char(string='Descripción del campo')
    tipo = fields.Char(string='Tipo de dato')

