# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)

class payment_acquirer_payu(models.Model):
    _inherit = 'payment.acquirer' 

    provider = fields.Selection(selection_add=[('payu', 'Payu')])
    payu_merchant_id = fields.Char(string='ID Mercantil', required_if_provider='payu')
    payu_account_id = fields.Char(string='ID Cuenta', required_if_provider='payu')
    payu_api_key = fields.Char(string='Clave API', required_if_provider='payu')
    payu_login = fields.Char(string='Login API', required_if_provider='payu')

    def render(self, reference, amount, currency_id, partner_id=False, values=None):
        response = super(payment_acquirer_payu, self).render(reference, amount, currency_id, partner_id, values)
        _logger.warning("reference")
        _logger.warning(reference)
        _payment_transaction = self.env["payment.transaction"].search([('reference','=',reference)], limit=1)
        _logger.warning(_payment_transaction.acquirer_id.provider)
        if(_payment_transaction):
            if(_payment_transaction.acquirer_id.provider == "payu"):
                _payment_transaction.sudo().update({
                                                        'payu_response': 'En espera...',
                                                        'payu_trans_order_ref': request.session['reference_code']
                                                    })
                _logger.warning("transaction unlinked")
        return response