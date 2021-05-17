# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    @api.onchange('state_id','country_id','cities')
    def cityfilter(self):
        if self.cities:
            return {'domain': {'cities': [('state_id', '=?', self.state_id.id)],'postal_id': [('city_id', '=?', self.cities.id)]}}
        elif self.state_id:
            return {'domain': {'cities': [('state_id', '=?', self.state_id.id)],'postal_id': [('state_id', '=?', self.state_id.id)]}}
        elif self.country_id:
            return {'domain': {'cities': [('state_id', '=', False)],'postal_id': [('country_id', '=?', self.country_id.id)]}}
        else:
            return {'domain': {'cities': [('state_id', '!=', False)],'postal_id': [('state_id', '!=', False)]}}

    cities = fields.Many2one('l10n_co_cities.city', context="{'default_state_id': state_id}")
    postal_id = fields.Many2one('l10n_co_postal.postal_code', context="{'default_state_id': state_id}")
    count = fields.Integer('auxiliar de cambios')

    @api.onchange('parent_id')
    def onchange_parent_id_cities(self):
        self.cities = self.parent_id.cities

    @api.onchange('postal_id')
    def onchange_postal_id(self):
        self.zip = self.postal_id.name
        if self.postal_id:
            self.cities = self.postal_id.city_id

    @api.onchange('country_id')
    def update_country(self):
        if self.count<=0:
            self.cities = None
            self.state_id = None
            self.postal_id = None
            self.count+=1

    @api.onchange('state_id')
    def update_state(self):
        if self.count<=0:
            self.cities = None
            self.postal_id = None
            self.count+=1

    @api.onchange('cities')
    def update_cities(self):
        if not self.cities:
            self.postal_id = None
        else:
            self.state_id = self.cities.state_id
            self.count +=1