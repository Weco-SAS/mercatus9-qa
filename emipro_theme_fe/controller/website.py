# -*- coding: utf-8 -*-
from odoo import http

class emipro_fe(http.Controller):


    @http.route('/emipro_fe/index', methods=['POST'], type='json')
    def index(self, **kw):
        pass
