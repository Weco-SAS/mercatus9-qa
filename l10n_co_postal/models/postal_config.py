# -*- encoding: utf-8 -*-
from enum import Enum

from odoo import models, api, fields
import logging
import json
import os

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ConfigCP(Enum):
    postal_ciudad = 'postal_ciudad'
    postal_departamento = 'postal_departamento'
    postal_pais = 'postal_pais'


class hr_config(models.TransientModel):
    _inherit = 'res.config.settings'

    cp_data = None

    def generar_filtros_cp(self):
        if self.env['res.config.settings'].search([('company_id', '=', self.env.user.company_id.id)], order="id desc",limit=1).chart_template_id:
            self.cp_data = self._load_config_postal_data()
            country_field = self.cp_data[ConfigCP.postal_pais.name]
            state_field = self.cp_data[ConfigCP.postal_departamento.name]
            city_field = self.cp_data[ConfigCP.postal_ciudad.name]
            try:
                path = 'data/postal_code.json'
                root_directory = os.getcwd()
                dir = os.path.dirname(__file__)
                if root_directory != '/' and '/' in root_directory:
                    file_dir = dir.replace(root_directory, '').replace('models', '')
                else:
                    file_dir = dir.replace('models', '')
                route = file_dir + path
                if route[0] == '/':
                    with open(route[1:]) as file:
                        data = json.load(file)
                else:
                    with open(route[0:]) as file:
                        data = json.load(file)

                for postal in data['postal_codes']:
                    und_cod_postal = self.env['l10n_co_postal.postal_code'].search([('name', '=', postal['name'])])
                    country_id = self.env[country_field.config_cp_detail_id.tipo].search([(country_field.field_name, '=', postal['country_code'])],limit=1)
                    state_id = self.env[state_field.config_cp_detail_id.tipo].search([(state_field.field_name, '=', postal['state_code'])],limit=1)
                    city_id = self.env[city_field.config_cp_detail_id.tipo].search([(city_field.field_name, '=', postal['city_code'])],limit=1)
                    und_cod_postal.write({'state_id': state_id.id, 'city_id': city_id.id, 'country_id': country_id.id })
                file.close()

            except Exception as e:
                _logger.error('Error actualizando los datos de postal_code - {}'.format(e))
                raise ValidationError('Error actualizando los datos de postal_code - {}'.format(e))

    def _get_postal_config(self):
        return self.env['l10n_co_postal.config_cp'].search([], limit=1)

    def _unload_config_postal_data(self):
        self.cp_data = None

    def _load_config_postal_data(self):
        for postal in self:
            config_cp = postal._get_postal_config()
            self.cp_data = {
                ConfigCP.postal_ciudad.name: config_cp.get_value(
                    field_name=ConfigCP.postal_ciudad.name,
                    obj_id=postal.id
                ),
                ConfigCP.postal_departamento.name: config_cp.get_value(
                    field_name=ConfigCP.postal_departamento.name,
                    obj_id=postal.id
                ),
                ConfigCP.postal_pais.name: config_cp.get_value(
                    field_name=ConfigCP.postal_pais.name,
                    obj_id=postal.id
                )
            }
        return self.cp_data
