# -*- coding: utf-8 -*-

import json
import requests

#  PayU Testing data:
MERCHANT_ID = '500238'
ACCOUNT_ID = '500547'
API_LOGIN = '11959c415b33d0c'
API_KEY = '6u39nqhq8ftd0hlvnjfs66eh8c'
PUBLIC_KEY = 'PK186ijn7a2R137B52ZHHm1P9P'
PAYMENTS_URL = 'https://api.payulatam.com/payments-api/4.0/service.cgi'
REPORTS_URL = 'https://api.payulatam.com/reports-api/4.0/service.cgi'
TOKENIZE_URL = 'http://api.payulatam.com/payments-api/4.0/service'
TEST = False
REPORTS='reports'
PAYMENTS='payments'

import logging
_logger = logging.getLogger(__name__)


class PayU(object):
    def __init__(self, api_login='', api_key='', account_id=''):
        """ Datos de la cuenta de PayU necesarios para usar la API"""

        self.api_login = api_login if api_login else API_LOGIN
        self.api_key = api_key if api_key else API_KEY
        self.account_id = account_id  if account_id else ACCOUNT_ID
        self.payments_url = PAYMENTS_URL
        self.reports_url = REPORTS_URL
        self.test = TEST

        # Default data for every request
        self.payload = {
            'language': 'es',
            'command': 'PING',
            'merchant': {
                'apiLogin': self.api_login,
                'apiKey': self.api_key
            },
            'test': self.test
        }

        self.order = {
            'language': 'es',
            'accountId': self.account_id
        }

        self.transaction_data = {
            'type': 'AUTHORIZATION_AND_CAPTURE',
            'paymentCountry': 'MX',
        }


        self.payment_data = {
           
        }

    def send_request(self, payload, api_type=PAYMENTS):
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }

        payu_url = self.payments_url
        if api_type == REPORTS:
            payu_url = self.reports_url
        
        _logger.warning("PAYMENT_PREFERENCE")
        _logger.warning(headers)
        _logger.warning(payu_url)
        _logger.warning(payload)
                
        response = requests.post(
            payu_url,
            data=json.dumps(payload),
            headers=headers,
            verify=False
        )
        
        _logger.warning("response.json()")
        _logger.warning(response.json())
        
        print ('REQUEST: %s' % payload)
        print ('RESPONSE: %s' % json.dumps(response.text, indent=2))
        return response

    def create_token(self,
                     payer_id,
                     full_name,
                     payment_method,
                     card_number,
                     expiration_date):

        payload = self.payload.copy()

        payload.update({
            'command': 'CREATE_TOKEN',
            'creditCardToken': {
                'payerId': payer_id,
                'name': full_name,
                'paymentMethod': payment_method,
                'number': card_number,
                'expirationDate': expiration_date
            }
        })

        response = self.send_request(payload)
        return json.loads(response.text)

    def get_tokens(self, payer_id, token_id):
        """ Información sobre el token """

        payload = self.payload.copy()

        payload.update({
            'command': 'GET_TOKENS',
            'creditCardTokenInformation': {
                'payerId': payer_id,
                'creditCardTokenId': token_id,
                "startDate": "2014-01-15T15:30:00",
                "endDate": "2015-01-16T17:40:00"
            }
        })

        response = self.send_request(payload)

        return json.loads(response.text)
    
    def get_payment(self, transaction_id):
        """ Información sobre el token """

        payload = self.payload.copy()
        payload.update({
            'command': 'TRANSACTION_RESPONSE_DETAIL',
            'details': {
                "transactionId": transaction_id
            }
        })

        response = self.send_request(payload)

        return json.loads(response.text)

    def submit_transaction(self,
                           token_id,
                           reference_code,
                           description,
                           notify_url,
                           value,
                           email):

        order = self.order.copy()

        order.update({
            'referenceCode': reference_code,
            'description': description,
            'signature': '2b241ad76d4e4eb37cf9113fa9aae8df',
            'notifyUrl': notify_url,
            'additionalValues': {
                'TX_VALUE': {
                    'value': value,
                    'currency': 'MXN'
                }
            }
        })

        transaction = self.transaction_data.copy()
        transaction.update({
            'order': order,
            'creditCardTokenId': token_id,
            'payer':{
                'emailAddress': email
            }
        })

        payload = self.payload.copy()

        payload.update({
            'command': 'SUBMIT_TRANSACTION',
            'transaction': transaction
        })

        response = self.send_request(payload)
        return json.loads(response.text)

    def order_detail(self, order_id):
        payload = self.payload.copy()
        payload.update({
            'command': 'ORDER_DETAIL',
            'details':{
                'orderId': order_id
            }
        })

        response = self.send_request(payload, api_type=REPORTS)
        return json.loads(response.text)
    
    def order_detail_referenced(self, reference):
        payload = self.payload.copy()
        payload.update({
            'command': 'ORDER_DETAIL_BY_REFERENCE_CODE',
            'details':{
                'referenceCode': reference
            }
        })

        response = self.send_request(payload, api_type=REPORTS)
        return json.loads(response.text)