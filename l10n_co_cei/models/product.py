#-*- coding:utf-8 -*-
from odoo import models, api, _, fields
from odoo.exceptions import ValidationError
import logging


class currency(models.Model):
    _inherit = ['product.template']

    enable_charges = fields.Boolean(
        string='Cargo de Factura Electrónica',
    )