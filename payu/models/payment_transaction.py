# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.addons.payu.models.payu import PayU
import os, hashlib, decimal, datetime, re, json, sys
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)

class payment_transaction(models.Model):
    _inherit = 'payment.transaction'

    payu_response = fields.Html( string="PayuLatam")
    payu_trans_id = fields.Char( string="Trans ID")
    payu_trans_order_ref = fields.Char( string="Order Ref")

    def _payu_reponse_formatter(self, _transaction):
        _response_html = str("<div>")
        
        if(_transaction['paymentMethod']):
            _response_html = _response_html + str("<div class='payu-response-row'>")
            _response_html = _response_html + str("<label>")
            _response_html = _response_html + str("Método: ")
            _response_html = _response_html + str("</label>")
            _response_html = _response_html + str("<span>")
            _response_html = _response_html + str(_transaction['paymentMethod'])
            _response_html = _response_html + str("</span>")
            _response_html = _response_html + str("</div>")
        
        if('id' in _transaction):
            _response_html = _response_html + str("<div class='payu-response-row'>")
            _response_html = _response_html + str("<label>")
            _response_html = _response_html + str("Transacción: ")
            _response_html = _response_html + str("</label>")
            _response_html = _response_html + str("<div><span>")
            _response_html = _response_html + str("ID: ")+str(_transaction['id'])
            _response_html = _response_html + str("</span></div>")
            _response_html = _response_html + str("</div>")

        _response_html = _response_html + str("</div>")

        return _response_html
    
    def action_send_notification(self, _id, _record_name, _transaction, message=None):
        _mail_messages = self.env['mail.message'].sudo().search([('res_id', '=', _id), ('body', 'ilike', str(_transaction.payu_response))])        
        if(_mail_messages):
            for _mail_message in _mail_messages:                
                mail_message = self.env['mail.message'].sudo().browse(int(_mail_message.id))
                if(message):
                    mail_message.env.cr.commit()
                    mail_message.env.cr.rollback()
                    mail_message.sudo().update({'body': str(mail_message.body) + str("<br>") + str(message)})
        else:
            mail_message_values = {
                                        'email_from': self.env.user.partner_id.email,
                                        'author_id': self.env.user.partner_id.id,
                                        'model': 'sale.order',
                                        'message_type': 'comment',
                                        'body': str("<br>") + str(message),
                                        'res_id': _id,
                                        'subtype_id': self.env.ref('mail.mt_comment').id,
                                        'record_name': _record_name,
                                    }
            self.env['mail.message'].sudo().create(mail_message_values)

    
    def payu_confirm(self):
        try:
            payment_acquirer = self.env['payment.acquirer'].search([('provider','=','payu')], limit=1)
            payment_acquirer = self.env['payment.acquirer'].browse(payment_acquirer.id)

            _test = False
            if(str(payment_acquirer.state)=="test"):
                _test = True

            payment_transactions = self.env['payment.transaction'].search([('state','!=','done'),('acquirer_id', '=', payment_acquirer.id)])

            client = PayU(payment_acquirer.payu_login, payment_acquirer.payu_api_key, payment_acquirer.payu_merchant_id)
            
            for payment_transaction in payment_transactions:
                
                query = "select * from sale_order_transaction_rel where transaction_id = " + str(payment_transaction.id) + str(" limit 1")
                self.env.cr.execute(query)
                sale_order_transaction_rel = self.env.cr.dictfetchone()

                o_order = self.env['sale.order'].browse(int(sale_order_transaction_rel['sale_order_id']))
                transaction = client.order_detail_referenced(str(o_order.last_reference)) 
                
                if(str(transaction['code']) == "SUCCESS"):
                    if('payload' in transaction['result']):
                        if( transaction['result']['payload'] != None ):
                            payu_transactions = transaction['result']['payload'][0]['transactions']

                            for payu_transaction in payu_transactions:
                                    odoo_transaction = self.env['payment.transaction'].sudo().search([('payu_trans_order_ref','=',str(o_order.last_reference))], limit=1)
                                    odoo_transaction = self.env['payment.transaction'].sudo().browse(odoo_transaction.id)
                                    payu_trans_state = payu_transaction['transactionResponse']['state']
                                    
                                    # payu_trans_state = "APPROVED"
                                    
                                    order_ref = str(odoo_transaction.reference).split("/")[0]
                                    sale_order = self.env['sale.order'].search([('name','!=',order_ref)],limit=1)
                                    o_order = self.env['sale.order'].browse(sale_order.id)
                                    
                                    if(payu_trans_state == "APPROVED"):
                                        
                                        # for orders
                                        if(str(o_order.payu_response).find('Aprobada')>0):
                                            pass
                                        else:
                                            html_trans_info = str('<div class="payu-response-row"><label>Estado: </label><span>Transacción Aprobada!</span></div>')
                                            payu_response = str(html_trans_info) + str(o_order.payu_response)
                                            o_order.sudo().update({'state':'sale'})
                                            o_order.sudo().write({'state':'sale'})

                                        # for transactions
                                        if(str(odoo_transaction.payu_response).find('Aprobada')>0):
                                            pass
                                        else:
                                            html_trans_info = str('<div class="payu-response-row"><label>Estado: </label><span>Transacción Aprobada!</span></div>')
                                            payu_response = str(html_trans_info) + str(self._payu_reponse_formatter(payu_transaction)) + str(odoo_transaction.payu_response)
                                            _payu_response = str(html_trans_info) + str(self._payu_reponse_formatter(payu_transaction))
                                            odoo_transaction.sudo().write({'payu_response':payu_response})
                                            odoo_transaction.sudo().write({'state':'done'})
                                            o_order.sudo().write({'payu_response':_payu_response})
                                            self.action_send_notification(o_order.id, o_order.name, odoo_transaction, _payu_response)

                                    if(payu_trans_state==str("PENDING")):
                                        html_trans_info = str('<div class="payu-response-row"><label>Estado: </label><span>Transacción Pendiente</span></div>')
                                        payu_response = str(html_trans_info) + str(self._payu_reponse_formatter(payu_transaction)) + str(odoo_transaction.payu_response)
                                        _payu_response = str(html_trans_info) + str(self._payu_reponse_formatter(payu_transaction))
                                        odoo_transaction.sudo().update({'state':'pending'})
                                        if(str(odoo_transaction.payu_response).find('Pendiente')>0):
                                            pass
                                        else:
                                            odoo_transaction.sudo().update({'payu_response':payu_response})
                                            odoo_transaction.sudo().write({'payu_response':payu_response})
                                            sale_order.sudo().update({'payu_response':payu_response})
                                            self.action_send_notification(o_order.id, o_order.name, odoo_transaction, _payu_response)
                                        sale_order.sudo().update({'state':'sale'})
                                        sale_order.sudo().write({'state':'sale'})

                                    if(payu_trans_state==str("REJECTED")):
                                        html_trans_info = str('<div class="payu-response-row"><label>Estado: </label><span>Transacción Rechazada</span></div>')
                                        payu_response = str(html_trans_info) + str(self._payu_reponse_formatter(payu_transaction)) + str(odoo_transaction.payu_response)
                                        _payu_response = str(html_trans_info) + str(self._payu_reponse_formatter(payu_transaction))
                                        odoo_transaction.sudo().update({'state':'cancel'})
                                        odoo_transaction.sudo().write({'state':'cancel'})
                                        if(str(odoo_transaction.payu_response).find('Rechazada')>0):
                                            pass
                                        else:
                                            odoo_transaction.sudo().update({'payu_response':payu_response})
                                            self.action_send_notification(o_order.id, o_order.name, odoo_transaction, _payu_response)
                                        sale_order.sudo().update({'state':'draft'})
                                        ale_order.sudo().write({'state':'draft'})
                                    
                                    if(payu_trans_state==str("IN_PROGRESS")):
                                        html_trans_info = str('<div class="payu-response-row"><label>Estado: </label><span>Transacción en Progreso</span></div>')
                                        payu_response = str(html_trans_info) + str(self._payu_reponse_formatter(payu_transaction)) + str(odoo_transaction.payu_response)
                                        _payu_response = str(html_trans_info) + str(self._payu_reponse_formatter(payu_transaction))
                                        odoo_transaction.sudo().update({'state':'cancel'})
                                        odoo_transaction.sudo().write({'state':'cancel'})
                                        if(str(odoo_transaction.payu_response).find('Progreso')>0):
                                            pass
                                        else:
                                            odoo_transaction.sudo().update({'payu_response':payu_response})
                                            self.action_send_notification(o_order.id, o_order.name, odoo_transaction, _payu_response)
                                        sale_order.sudo().update({'state':'sale'})
                                        sale_order.sudo().write({'state':'sale'})
        except Exception as e:
           exc_traceback = sys.exc_info()
           _logger.warning("CRON JOB - payu_confirm")
           _logger.warning(getattr(e, 'message', repr(e))+" ON LINE "+format(sys.exc_info()[-1].tb_lineno)) 

