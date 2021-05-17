# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from werkzeug import urls
import os, hashlib, decimal, datetime, re, json
import werkzeug
from odoo.addons.payu.models.payu import PayU

import logging
_logger = logging.getLogger(__name__)

# 5406 2545 8871 3208
class payu_controller(http.Controller):
    formsPath = str(os.path.dirname(os.path.abspath(__file__))).replace("controllers","")

    @http.route('/payu/get_payu_acquirer/', methods=['POST'], type='json', auth="public", website=True)
    def get_payu_acquirer(self, **kw):       
        response = {"acquirer":None,"form_bill":None}                
        query = "select name, website_id,company_id, state, payu_merchant_id, payu_account_id, payu_api_key from payment_acquirer where provider = 'payu' limit 1"
        request.cr.execute(query)    
        acquirer = request.cr.dictfetchone()
        form_bill = self.file_get_contents(str(self.formsPath)+str("/static/src/form/bill.html"))       
        response = {"acquirer":acquirer,"form_bill":form_bill}
        return response
    
    def generate_signature(self, values):
        data = '~'.join([
            values['payu_api_key'],
            values['payu_merchant_id'],
            values['order_name'],
            values['amount'],
            values['currency']])
        m = hashlib.md5()
        m.update(data.encode("utf8"))
        return m.hexdigest()
    
    @http.route('/payu/get_sale_order/', methods=['POST'], type='json', auth="public", website=True)
    def get_sale_order(self, **kw): 
        _logger.warning("INTO GAMER")
        params = {}
        params['acquirer_id'] = kw.get('acquirer_id')            
        params['partner_id'] = kw.get('partner_id')
        params['online_payment'] = kw.get('online_payment')
                       
        query = "select name, website_id,company_id, state, payu_merchant_id, payu_account_id, payu_api_key from payment_acquirer where provider = 'payu' limit 1"
        request.cr.execute(query)    
        acquirer = request.cr.dictfetchone()   
         
        if(acquirer['state']=="test"):
            state = str('1')
        else:
            state = str('0')

        if(params['online_payment']=="no"):
            query = "select id, name, amount_total, amount_tax, date_order, partner_shipping_id, amount_delivery from sale_order where partner_id = '"+str(params['partner_id'])+"' and state = '"+str('draft')+"' order by date_order desc limit 1"
        if(params['online_payment']=="yes"):
            query = "select id, name, amount_total, amount_tax, date_order, partner_shipping_id, amount_delivery from sale_order where partner_id = '"+str(params['partner_id'])+"' and state = '"+str('sent')+"' and require_payment = True order by date_order desc limit 1"

        request.cr.execute(query)    
        draft_order = request.cr.dictfetchone()

        request.session['order_id'] = str(draft_order["id"])
        

        _logger.warning("order_id_")
        _logger.warning(request.session['order_id'])

        query = "select name, currency_id from sale_order_line where order_id = "+str(draft_order["id"])
        request.cr.execute(query)    
        draft_order_lines = request.cr.dictfetchall()
        index = 1
        order_description = str("")
        currency_id = None
        for order_line in draft_order_lines:
            currency_id = order_line["currency_id"]
            order_description = str(order_description) + str("          ") + str(index) + str(". ") + str(order_line['name'])
            index = index + 1
        order_description = str(order_description)[:200]
       
        query = "select res_partner.id, res_partner.name, res_partner.vat, res_partner.phone, res_partner.email, res_partner.street, res_partner.city, res_partner.zip, res_partner.lang, res_country.name as country_name, res_country.code as country_code, res_country_state.name as state_name, res_currency.name as currency_name, res_currency.symbol as currency_symbol from res_partner left join res_country on res_country.id = res_partner.country_id left join res_country_state on res_country_state.id = res_partner.state_id left join res_currency on res_country.currency_id = res_currency.id   where res_partner.id = '"+str(draft_order['partner_shipping_id'])+"' limit 1"
        request.cr.execute(query)    
        res_partner_shipping = request.cr.dictfetchone()

        query = "select id, name from res_currency where id = " + str(currency_id) + " limit 1"
        request.cr.execute(query)    
        currency = request.cr.dictfetchone()
  
        if(draft_order):
            amount_total = float(draft_order['amount_total'])
            _logger.warning(amount_total)
            cents = decimal.Decimal('.01')
            parts_amount = str(amount_total).split(".")
            if(int(parts_amount[1])==0):
                parts_amount[1] = str("00")
            if(len(parts_amount[1])<2):
                parts_amount[1] = parts_amount[1]+'0'
                
            amount = str(int(decimal.Decimal(amount_total).quantize(cents, decimal.ROUND_HALF_UP)))            
            amount = parts_amount[0]+str(parts_amount[1])
            if(int(parts_amount[0])==0):
                amount = str(parts_amount[1])
            
            _logger.warning(parts_amount)
            
            order_name = str(datetime.datetime.now())
            order_name = re.sub('[^0-9]','', order_name)
            order_name = order_name[-9:]
            request.session['reference_code'] = str(draft_order['name']) + str(order_name)

            values = {
                        "payu_api_key":acquirer['payu_api_key'],
                        "payu_merchant_id":acquirer['payu_merchant_id'],
                        "order_name":str(draft_order['name'])+str(order_name),
                        "amount":format(float(amount_total), '.2f'), 
                        "currency": currency["name"]
                     }
            
            signature_digested = self.generate_signature(values)

            # base url
            query = "select value from ir_config_parameter where key = 'web.base.url' limit 1"
            request.cr.execute(query)
            ir_config_parameter = request.cr.dictfetchone()
            base_url = ir_config_parameter['value']
            
            __order = request.env['sale.order'].sudo().browse(int(draft_order['id']))
            __order.sudo().update({'last_reference': str(draft_order['name'])+str(order_name)})
            
            return {
                        'status' :  "OK",
                        'state':state,
                        'name' : res_partner_shipping['name'],
                        'phone' : res_partner_shipping['phone'],
                        'email' : res_partner_shipping['email'],
                        'address' : res_partner_shipping['street'],
                        'city' : res_partner_shipping['city'],
                        'state' : res_partner_shipping['state_name'],
                        'country_code':res_partner_shipping['country_code'],
                        'country_name':res_partner_shipping['country_name'],
                        'zip':res_partner_shipping['zip'],
                        'acquirer':acquirer['name'],  
                        'payu_merchant_id':acquirer['payu_merchant_id'],
                        'payu_account_id':acquirer['payu_account_id'],
                        'order_id':draft_order['id'],
                        'order_name':order_name,
                        'order_name_odoo':draft_order['name'],
                        'order_description':order_description,
                        'date_order':draft_order['date_order'],
                        'amount':format(float(amount_total), '.2f'),
                        'tax':str('0.00'),#draft_order['amount_tax'],
                        'tax_return_base':str('0'),
                        'currency_name':res_partner_shipping['currency_name'],
                        'currency_symbol':res_partner_shipping['currency_symbol'],
                        'signature':signature_digested,
                        'parts_amount':parts_amount,
                        'extra1':order_description,
                        'payer_document':res_partner_shipping['vat'],
                        'response_url':urls.url_join(base_url, '/shop/process_payu_payment'),
                        'end_point_url':self._get_end_point(state),
                    }
    
    @http.route('/shop/process_payu_payment', csrf=False, auth="public", website=True)    
    def process_payu_payment(self, **kw):
        _response = {}
        #transaction
        _response['lapTransactionState'] = kw.get('lapTransactionState')
        _response['message'] = kw.get('message')
        _response['reference_pol'] = kw.get('reference_pol')
        _response['transactionId'] = kw.get('transactionId')
        _response['description'] = kw.get('description')
        # cards
        _response['lapResponseCode'] = kw.get('lapResponseCode')
        _response['description'] = kw.get('description')
        _response['lapPaymentMethod'] = kw.get('lapPaymentMethod')
        _response['lapPaymentMethodType'] = kw.get('lapPaymentMethodType')
        # pse banks
        _response['pseBank'] = kw.get('pseBank')
        _response['pseReference1'] = kw.get('pseReference1')
        _response['pseReference2'] = kw.get('pseReference2')
        _response['pseReference3'] = kw.get('pseReference3')
        _response['pseCus'] = kw.get('cus')
        _response_html = self._payu_reponse_formatter(_response)  

        authorizationResult = _response['lapTransactionState']
        errorMessage = kw.get('lapResponseCode')

        _logger.warning('authorizationResult')
        _logger.warning(authorizationResult)

        if(authorizationResult==str("APPROVED") or authorizationResult==str("PENDING") or authorizationResult==str("REJECTED") or authorizationResult==str("IN_PROGRESS")):
            if('sale_order_id' in request.session or 'order_id' in request.session):
                current_sale_order_id = None 
                if(request.session['sale_order_id']):
                    current_sale_order_id = request.session['sale_order_id']
                if(request.session['order_id']):
                    current_sale_order_id = request.session['order_id']

                sale_order = http.request.env['sale.order'].sudo().search([['id','=',current_sale_order_id]])
                
                draft_order_lines = http.request.env['sale.order.line'].sudo().search([['order_id','=',sale_order.id]]) 

                currency_id = None 
                for order_line in draft_order_lines:
                    currency_id = order_line.currency_id.id

                if(authorizationResult==str("APPROVED")):
                    sale_order.action_done()
                else:
                    sale_order.action_confirm()
                
                sale_order.sudo().update({'payu_response':_response_html})

                query = "select * from payment_acquirer where provider = 'payu' limit 1"
                request.cr.execute(query)
                acquirer = request.cr.dictfetchone()

                _logger.warning("IN1")
                acquirer_id = False
                if(acquirer['id']):
                    _logger.warning("IN2")
                    acquirer_id = acquirer['id']

                    client = PayU(acquirer['payu_login'], acquirer['payu_api_key'], acquirer['payu_merchant_id'])
                    transaction = client.order_detail(int(_response['reference_pol']))

                    payment_transaction = request.env['payment.transaction'].sudo().search(
                                                                                                [('payu_trans_order_ref', 'ilike', str(transaction['result']['payload']['referenceCode']))], 
                                                                                                order='create_date desc', 
                                                                                                limit=1
                                                                                            )
                    
                    payment_transaction = request.env['payment.transaction'].sudo().browse(payment_transaction.id)
                    payment_transaction.sudo().update({ 
                                                        'payu_response': _response_html, 
                                                        'payu_trans_id': _response['transactionId'], 
                                                        'payu_trans_order_ref': transaction['result']['payload']['referenceCode'] 
                                                      })
                    
                    if(authorizationResult==str("PENDING") or authorizationResult==str("IN_PROGRESS")):
                        payment_transaction.sudo().update({'state':'pending'})
                        sale_order.sudo().update({'state':'sale'})
                        self.action_send_notification(sale_order.id, sale_order.name, payment_transaction, _response_html)
                        request.website.sale_reset()
                    
                    if(authorizationResult==str("REJECTED")):
                        payment_transaction.sudo().update({'state':'cancel'})
                        sale_order.sudo().update({'state':'sale'})
                        self.action_send_notification(sale_order.id, sale_order.name, payment_transaction, _response_html)
                    
                    if(authorizationResult==str("APPROVED")):
                        payment_transaction.sudo().update({'state':'done'})
                        self.action_send_notification(sale_order.id, sale_order.name, payment_transaction, _response_html)
                        request.website.sale_reset()                        
                          
                    uid = http.request.env.context.get('uid')
                    
                    sale_order = request.env["sale.order"].sudo().browse(sale_order.id)
                    sharable = sale_order._get_share_url(redirect=True)

                    if (not uid):
                        return werkzeug.utils.redirect("/my/orders/"+str(sale_order.id)+"?access_token="+str(sale_order.access_token))
                    else:
                        return werkzeug.utils.redirect("/shop/confirmation")
                else:
                    return werkzeug.utils.redirect("/shop/payment")
            else:
                return werkzeug.utils.redirect("/shop/payment")                          
        else:
            return werkzeug.utils.redirect("/shop/payment?authorizationResult="+str(authorizationResult)+"&errorMessage="+str(errorMessage))       
    
    def file_get_contents(self, filename):
        with open(filename) as f:
            return f.read()

    def file_put_contents(self, filename,data):
        with open(filename) as f:
            return f.write(data)
    
    def _get_end_point(self, state):
        if state == '0':
            return str('https://checkout.payulatam.com/ppp-web-gateway-payu')
        else:
            return str('https://sandbox.checkout.payulatam.com/ppp-web-gateway-payu')
    
    def _payu_reponse_formatter(self, _response):

        _statusText = {
                        "APPROVED":"Transacción aprobada",
                        "DECLINED":"Transacción rechazada",
                        "ERROR":"Error procesando la transacción",
                        "EXPIRED":"Transacción expirada",
                        "PENDING":"Transacción pendiente o en validación",
                        "SUBMITTED":"Transacción enviada a la entidad financiera y por algún motivo no terminó su procesamiento. Sólo aplica para la API de reportes"
                      } 

        if(_response['lapPaymentMethodType']=="CREDIT_CARD"):
            _payment_method_icon = str("<span>Tarjeta de Crédito <i class='fa fa-credit-card'/></span>")
            _entity = str("<span>"+str(_response['lapPaymentMethod'])+"</span>")
        elif(_response['lapPaymentMethodType']=="CASH"):
            _payment_method_icon = str("<span>Efectivo <i class='fa fa-money'/></span>")
            _entity = str("<span>"+str(_response['lapPaymentMethod'])+"</span>")
        elif(_response['lapPaymentMethodType']=="REFERENCED"):
            _payment_method_icon = str("<span>Referenciado</span>")
            _entity = str("<span>"+str(_response['lapPaymentMethod'])+"</span>")
        elif(_response['lapPaymentMethodType']=="PSE"):
            _payment_method_icon = str("<span>PSE <i class='fa fa-bank'/></span>")
            _entity = str("<div><span>"+str(_response['pseBank'])+"</span></div>")
            if(_response['pseCus']!=''):
                _entity = _entity + str("<div><label>CUS: <label><span>"+str(_response['pseCus'])+"</span></div>")
            if(_response['pseReference1']!=''):
                _entity = _entity + str("<div><label>Ref 1: <label><span>"+str(_response['pseReference1'])+"</span></div>")
            if(_response['pseReference2']!=''):
                _entity = _entity + str("<div><label>Ref 2: <label><span>"+str(_response['pseReference2'])+"</span></div>")
            if(_response['pseReference3']!=''):
                _entity = _entity + str("<div><label>Ref 3: <label><span>"+str(_response['pseReference3'])+"</span></div>")
        else:
            _payment_method_icon = str("<span>") + str(_response['lapPaymentMethod']) +  str("</span>")

        _response_html = str("<div>")
        
        # row state
        _response_html = _response_html + str("<div class='payu-response-row state-payu-trans'>")
        _response_html = _response_html + str("<label>")
        _response_html = _response_html + str("Estado: ")
        _response_html = _response_html + str("</label>")
        _response_html = _response_html + str("<span>")
        _response_html = _response_html + str(_statusText[""+str(_response['lapTransactionState'])+""])
        _response_html = _response_html + str("</span>")

        if(_response['lapResponseCode']!=''):
            _response_html = _response_html + str("<div><span>"+str(str(_response['lapResponseCode']).replace('_',' ')).capitalize()+"</span></div>")
        _response_html = _response_html + str("</div>")

        #row state code
        _response_html = _response_html + str("<div class='payu-response-row'>")
        _response_html = _response_html + str("<label>")
        _response_html = _response_html + str("Método: ")
        _response_html = _response_html + str("</label>")
        _response_html = _response_html + str("<span>")
        _response_html = _response_html + str(_payment_method_icon)
        _response_html = _response_html + str("</span>")
        _response_html = _response_html + str("</div>")

        _response_html = _response_html + str("<div class='payu-response-row'>")
        _response_html = _response_html + str("<label>")
        _response_html = _response_html + str("Transacción: ")
        _response_html = _response_html + str("</label>")
        _response_html = _response_html + str("<div><span>")
        _response_html = _response_html + str("ID: ")+str(_response['transactionId'])
        _response_html = _response_html + str("</span></div>")
        _response_html = _response_html + str("<div><span>"+ str("REF: ")+str(_response['reference_pol'])+"</span></div>")
        _response_html = _response_html + str("</div>")

        # entity
        _response_html = _response_html + str("<div class='payu-response-row'>")
        _response_html = _response_html + str("<label>")
        _response_html = _response_html + str("Entidad: ")
        _response_html = _response_html + str("</label>")
        _response_html = _response_html + str("<span>")
        _response_html = _response_html + str(_entity)
        _response_html = _response_html + str("</span>")
        _response_html = _response_html + str("</div>")

        _response_html = _response_html + str("</div>")

        return _response_html
    
    def action_send_notification(self, _id, _record_name, _transaction, message=None):
        _mail_messages = request.env['mail.message'].sudo().search([('res_id', '=', _id), ('body', 'ilike', str(_transaction.payu_response))])
        _logger.warning("IN#0")
        _logger.warning(_mail_messages)
        if(_mail_messages):
            for _mail_message in _mail_messages:                
                mail_message = request.env['mail.message'].sudo().browse(int(_mail_message.id))
                if(message):
                    _logger.warning("IN#01")
                    mail_message.env.cr.commit()
                    mail_message.env.cr.rollback()
                    mail_message.sudo().update({'body': str(mail_message.body) + str("<br>") + str(message)})
        else:
            _logger.warning("IN#1")
            mail_message_values = {
                                        'email_from': request.env.user.partner_id.email,
                                        'author_id': request.env.user.partner_id.id,
                                        'model': 'sale.order',
                                        'message_type': 'comment',
                                        'body': str("<br>") + str(message),
                                        'res_id': _id,
                                        'subtype_id': request.env.ref('mail.mt_comment').id,
                                        'record_name': _record_name,
                                    }
            
            _logger.warning("IN#2")
            _logger.warning(mail_message_values)
            request.env['mail.message'].sudo().create(mail_message_values)
            _logger.warning("IN#3")