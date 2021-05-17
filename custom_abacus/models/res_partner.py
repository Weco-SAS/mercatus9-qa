from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    idioma_fe = fields.Many2one('res.lang', string='Idioma factura')


    # @api.onchange('idioma_fe')
    # def _onchange_lang(self):
    #     ctx = self.env.context.copy()
    #     ctx.update({
    #         'lang': self.idioma_fe.code,
    #     })
    #     self.env.context = ctx
    #     print(self.env.context)
