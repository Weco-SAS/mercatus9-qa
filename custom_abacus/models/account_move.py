from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    name = fields.Char(string='Label', translate=True)

    def _get_computed_name(self):
        self.ensure_one()

        if not self.product_id:
            return ''

        if self.partner_id.idioma_fe.code:
            ctx = self.env.context.copy()
            ctx.update({
                'lang': self.partner_id.idioma_fe.code,
            })
            self.env.context = ctx
            product = self.product_id.with_context(lang=self.partner_id.idioma_fe.code)
        else:
            product = self.product_id

        values = []
        if product.partner_ref:
            values.append(product.partner_ref)
        if self.journal_id.type == 'sale':
            if product.description_sale:
                values.append(product.description_sale)
        elif self.journal_id.type == 'purchase':
            if product.description_purchase:
                values.append(product.description_purchase)
        return '\n'.join(values)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' in vals and 'product_id' in vals and 'sale_line_ids' in vals:
                partner = self.env['res.partner'].browse(vals['partner_id'])
                if partner.idioma_fe.code:
                    ctx = self.env.context.copy()
                    ctx.update({
                        'lang': partner.idioma_fe.code,
                    })
                    self.env.context = ctx
                    product = self.env['product.product'].with_context(lang=partner.idioma_fe.code).browse(vals['product_id'])
                    values = []
                    if product.partner_ref:
                        values.append(product.partner_ref)
                    if product.description_sale:
                        values.append(product.description_sale)
                    vals['name'] = '\n'.join(values)
        lines = super(AccountMoveLine, self).create(vals_list)
        return lines



