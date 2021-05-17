# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import werkzeug

from odoo import http, tools, SUPERUSER_ID, _
from odoo.http import request
from odoo.addons.payment.controllers.portal import PaymentProcessing
_logger = logging.getLogger(__name__)

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteCODPayment(http.Controller):

    _accept_url = '/cod/payment/feedback'

    @http.route(['/cod/payment/feedback'], type='http', auth='none', csrf=False)
    def cod_form_feedback(self, **post):
        post.update({ 'return_url':'/shop/payment/validate' })
        _logger.info('Beginning form_feedback with post data %s', pprint.pformat(post))  # debug
        
        request.env['payment.transaction'].sudo().form_feedback(post, 'cod')
        return werkzeug.utils.redirect(post.pop('return_url', '/'))
    
    
    @http.route('/shop/payment/cod', type='json', auth="public", methods=['POST'], website=True)
    def codline(self, payment_id, **post):
        return True
    
    @http.route('/shop/payment/default', type='json', auth="public", methods=['POST'], website=True)
    def payment_default(self, payment_id, **post):      
        
        cr, uid, context = request.cr, request.uid, request.context
        
        return request.redirect('/shop/payment/validate')


class WebsiteCODPayment(WebsiteSale):

    @http.route('/shop/payment/validate', type='http', auth="public", website=True, sitemap=False)
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        if transaction_id:
            tx = request.env['payment.transaction'].sudo().browse(transaction_id)
            assert tx in order.transaction_ids()
        elif order:
            tx = order.get_portal_last_transaction()
        else:
            tx = None

        if not order or (order.amount_total and not tx):
            return request.redirect('/shop')

        if (not order.amount_total and not tx) or tx.state in ['pending', 'done', 'authorized']:
            if (not order.amount_total and not tx):
                # Orders are confirmed by payment transactions, but there is none for free orders,
                # (e.g. free events), so confirm immediately
                order.with_context(send_email=True).action_confirm()
        elif tx and tx.state == 'cancel':
            # cancel the quotation
            order.action_cancel()
        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset()
        if tx and tx.state == 'draft':
            return request.redirect('/shop')

        if tx.acquirer_id.provider == 'cod':
            payment_acquirer_obj = request.env['payment.acquirer'].sudo().search([('id','=', tx.acquirer_id.id)]) 
        
            product_obj = request.env['product.product']
            extra_fees_product = request.env['ir.model.data'].get_object_reference('bi_website_cash_on_delivery', 'product_product_fees')[1]
            product_ids = product_obj.sudo().search([('product_tmpl_id.id', '=', extra_fees_product)])
            
            order_line_obj = request.env['sale.order.line'].sudo().search([])
            
            
            flag = 0
            for i in order_line_obj:
                if i.product_id.id == product_ids.id and i.order_id.id == order.id:
                    flag = flag + 1
            
            if flag == 0:
                order_line_obj.sudo().create({
                        'product_id': product_ids.id,
                        'name': 'Extra Fees',
                        'price_unit': payment_acquirer_obj.delivery_fees,
                        'order_id': order.id,
                        'product_uom':product_ids.uom_id.id,
                    
                    })
                tx.update({
                    'fees' : payment_acquirer_obj.delivery_fees
                    })            

            order.action_confirm()
            email_act = order.action_quotation_send()
            email_ctx = email_act.get('context', {})
            order.with_context(**email_ctx).message_post_with_template(email_ctx.get('default_template_id'))
            
            request.website.sale_reset()            

        PaymentProcessing.remove_payment_transaction(tx)
        return request.redirect('/shop/confirmation')
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
