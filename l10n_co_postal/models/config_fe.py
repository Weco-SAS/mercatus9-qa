# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ConfigCP(models.Model):
    _name = 'l10n_co_postal.config_cp'
    _description = "parametros de configuracion campos de códigos postales"

    config_cp_detail_id = fields.Many2one(
        'l10n_co_postal.config_cp_details',
        string='Detalle Configuración',
        required=True
    )
    model_name = fields.Char(string='Nombre del modelo')
    field_name = fields.Char(string='Nombre del campo referenciado')

    @api.constrains('config_cp_detail_id')
    def _check_unique_config_cp_detail_id(self):
        config_cps = self.env['l10n_co_postal.config_cp'].search([])

        count = 0

        for config_cp in config_cps:
            if config_cp.config_cp_detail_id.id == self.config_cp_detail_id.id:
                count += 1

        if count > 1:
            raise ValidationError(
                "Solo es permitido un valor por detalle de configuración"
            )
    
    def get_value(self, field_name, obj_id, can_be_null=False):
        if not field_name:
            raise ValidationError("Parámetro 'field_name' no válido.")
        if not obj_id:
            raise ValidationError("Debe incluir un ID para la búsqueda.")

        config_cps = self.env['l10n_co_postal.config_cp'].search([])

        config_cp = None

        for conf in config_cps:
            if conf.config_cp_detail_id.name == field_name:
                config_cp = conf
                break
        
        if not config_cp:
            raise ValidationError("'field_name' (%s) no encontrado." % field_name)
        if not 'model_name' in config_cp:
            raise ValidationError("Nombre del modelo no configurado.")

        return config_cp
