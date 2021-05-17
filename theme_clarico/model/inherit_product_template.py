
# -*- encoding: utf-8 -*-
###############################################################################
#
#    Module Writen to Odoo13, Open Source Management Solution
#
############################################################################

from odoo import fields, models, api, _


class productTemplate(models.Model):
    _inherit = 'product.template'

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False,
                              parent_combination=False, only_template=False):

        record= super(productTemplate, self)._get_combination_info(combination=combination, product_id=product_id, add_qty=add_qty, pricelist=pricelist,
             parent_combination=parent_combination, only_template=only_template)

        if record['product_id'] != False:
            product_id= self.env['product.product'].browse(record['product_id'])
            try:
                display_name = product_id.name + ' (' + product_id.product_template_attribute_value_ids.name + ')'
            except TypeError:
                display_name = product_id.name
            record.update(display_name=display_name)
        return record