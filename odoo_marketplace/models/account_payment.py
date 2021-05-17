# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    partner_type = fields.Selection(selection_add=[("seller", "Seller")])

    @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id', 'payment_type')
    def _compute_payment_difference(self):
        draft_payments = self.filtered(lambda p: p.invoice_ids and p.state == 'draft')
        for pay in draft_payments:
            payment_amount = -pay.amount if pay.payment_type == 'outbound' else pay.amount
            pay.payment_difference = pay._compute_payment_amount(pay.invoice_ids, pay.currency_id, pay.journal_id, pay.payment_date) - payment_amount
            if self._context.get("active_model", False) == "seller.payment":
                pay.payment_difference = abs(self.env["seller.payment"].browse(
                    self._context["active_id"]).payable_amount) - pay.amount
        (self - draft_payments).payment_difference = 0

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        if self._context.get("active_model") == "account.move" and self._context.get('active_id'):
            invoice = self.env['account.move'].browse(self._context.get('active_id'))
            if invoice and invoice.is_seller and invoice.seller_payment_ids:
                rec["partner_type"] = "seller"
                rec["payment_type"] = "outbound"
        return rec

    def post(self):
        for rec in self:
            sequence_code = False
            if not rec.name and rec.payment_type != 'transfer' and rec.partner_type == 'seller':
                if rec.payment_type == 'inbound':
                    sequence_code = 'seller.payment.seller.refund'
                if rec.payment_type == 'outbound':
                    sequence_code = 'seller.payment.seller.invoice'
            if sequence_code:
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
        invoice_ids = self.mapped('invoice_ids')
        not_paid_invoices = invoice_ids.filtered(lambda move: move.is_invoice(include_receipts=True) and move.invoice_payment_state not in ('paid', 'in_payment'))
        result = super(AccountPayment, self).post()
        not_paid_invoices.filtered(lambda move: move.invoice_payment_state in ('paid', 'in_payment')).mp_post_action_invoice_paid()
        return result
