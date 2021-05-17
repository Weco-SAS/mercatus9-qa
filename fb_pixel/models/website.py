# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################


from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    fb_pixel_key = fields.Char('Facebook pixel ID')
