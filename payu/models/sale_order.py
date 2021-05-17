# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class sale_order(models.Model):
    _inherit = 'sale.order'

    payu_response = fields.Html( string="PayuLatam", default="Sin petición")
    last_reference = fields.Char( string="Reference Code")