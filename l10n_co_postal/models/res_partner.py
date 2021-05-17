# -*- coding: utf-8 -*-
import logging
import validators

from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    postal_id = fields.Many2one('l10n_co_postal.postal_code', string="Código Postal", default=1)