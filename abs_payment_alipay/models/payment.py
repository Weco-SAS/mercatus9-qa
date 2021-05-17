# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2020-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
import logging
import re
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.tools import float_compare
_logger = logging.getLogger(__name__)
from werkzeug import urls
from odoo.addons.payment_alipay.controllers.main import AlipayController


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def render_sale_button(self, order, submit_txt=None, render_values=None):
        values = {
            'partner_id': order.partner_id.id,
        }
        if render_values:
            values.update(render_values)
        # Not very elegant to do that here but no choice regarding the design.
        self._log_payment_transaction_sent()

        ##### If Alipay, Converted 'Amount' into 'USD' Currency
        if self.acquirer_id.provider == 'alipay':
            usd_currency = self.env.ref('base.USD')
            if usd_currency.id != order.pricelist_id.currency_id.id:
                return self.acquirer_id.with_context(submit_class='btn btn-primary', submit_txt=submit_txt or _('Pay Now')).sudo().render(
                    self.reference,
                    self.amount,
                    self.currency_id.id,
                    values=values,
                )
            else:
                return self.acquirer_id.with_context(submit_class='btn btn-primary', submit_txt=submit_txt or _('Pay Now')).sudo().render(
                    self.reference,
                    order.amount_total,
                    order.pricelist_id.currency_id.id,
                    values=values,
                )
        else:
            return self.acquirer_id.with_context(submit_class='btn btn-primary', submit_txt=submit_txt or _('Pay Now')).sudo().render(
                self.reference,
                order.amount_total,
                order.pricelist_id.currency_id.id,
                values=values,
            )


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    def _get_alipay_tx_values(self, values):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        alipay_tx_values = ({
            '_input_charset': 'utf-8',
            'notify_url': urls.url_join(base_url, AlipayController._notify_url),
            'out_trade_no': values.get('reference'),
            'partner': self.alipay_merchant_partner_id,
            'return_url': urls.url_join(base_url, AlipayController._return_url),
            'subject': values.get('reference'),
            'total_fee': values.get('amount') + values.get('fees'),
        })
        #If Alipay, update 'total_fee'
        if self.provider == 'alipay':
            alipay_tx_values.update({
                'total_fee': round(values.get('amount') + values.get('fees'),2),
            })
        if self.alipay_payment_method == 'standard_checkout':
            alipay_tx_values.update({
                'service': 'create_forex_trade',
                'product_code': 'NEW_OVERSEAS_SELLER',
                'currency': values.get('currency').name,
            })
        else:
            alipay_tx_values.update({
                'service': 'create_direct_pay_by_user',
                'payment_type': 1,
                'seller_email': self.alipay_seller_email,
            })
        sign = self._build_sign(alipay_tx_values)
        alipay_tx_values.update({
            'sign_type': 'MD5',
            'sign': sign,
        })
        return alipay_tx_values

