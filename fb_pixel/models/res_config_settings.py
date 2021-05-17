# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################


from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    has_fb_pixel = fields.Boolean(
        string="Facebook Pixel",
        config_parameter='fb_pixel.has_fb_pixel')
    fb_pixel_key = fields.Char(
        string='Pixel ID', 
        related='website_id.fb_pixel_key',
        readonly=False)

    @api.onchange('has_fb_pixel')
    def onchange_has_fb_pixel(self):
        if not self.has_fb_pixel:
            self.fb_pixel_key = False
