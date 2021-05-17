# -*- coding: utf-8 -*-
import logging
import validators

from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    fe_habilitada = fields.Boolean(
        string='Habilitar'
    )

    fe_primer_apellido = fields.Char(
        string='Primer apellido',
    )
    fe_segundo_apellido = fields.Char(
        string='Segundo apellido',
        default=''
    )
    fe_primer_nombre = fields.Char(
        string='Primer nombre',
    )
    fe_segundo_nombre = fields.Char(
        string='Segundo nombre',
        default=''
    )
    fe_razon_social = fields.Char(
        string='Razón social',
        default=''
    )
    fe_tipo_documento = fields.Selection(
        selection=[
            ('11', 'Registro civil'),
            ('12', 'Tarjeta de identidad'),
            ('13', 'Cédula de ciudadanía'),
            ('21', 'Tarjeta de extranjería'),
            ('22', 'Cédula de extranjería'),
            ('31', 'NIT'),
            ('41', 'Pasaporte'),
            ('42', 'Documento de identificación extranjero'),
            ('50', 'NIT de otro país'),
            ('91', 'NUIP'),
        ],
        string='Tipo de documento',
    )
    fe_nit = fields.Char(
        string='Número de documento',
    )
    fe_digito_verificacion = fields.Selection(
        selection=[
            ('0', '0'),
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('6', '6'),
            ('7', '7'),
            ('8', '8'),
            ('9', '9'),
            ('No aplica', 'No aplica'),
        ],
        string='Dígito de verificación',
        default='No aplica'
    )
    fe_es_compania = fields.Selection(
        selection=[
            ('1', 'Jurídica'),
            ('2', 'Natural'),
        ],
        string='Tipo de persona',
        default='1',
    )
    fe_tipo_regimen = fields.Selection(
        selection=[
            ('00', 'Simplificado'),
            ('02', 'Común'),
            ('03', 'No aplicable'),
            ('04', 'Simple'),
            ('05', 'Ordinario')
        ],
        string='Tipo de régimen',
        default='04',
    )
    fe_regimen_fiscal = fields.Selection(
        selection=[
            ('48', 'responsable del impuesto sobre las ventas – IVA'),
            ('49', 'No responsable de IVA')
        ],
        string='Régimen Fiscal',
        default='49',
    )
    fe_es_contribuyente = fields.Boolean(
        string='Gran contribuyente'
    )

    fe_matricula_mercantil = fields.Char(
        string='Matrícula mercantil',
        default='0'
    )

    fe_responsabilidad_fiscal = fields.Many2one(
        'l10n_co_cei_settings.responsabilidad_fiscal',
        string='Responsabilidad fiscal'
    )

    responsabilidad_fiscal_fe = fields.Many2many(
        'l10n_co_cei_settings.responsabilidad_fiscal',
        'l10n_co_cei_partner_rfiscal',
        'partner_id',
        'responsabilidad_id',
        string='Responsabilidad fiscal'
    )

    fe_destinatario_factura = fields.Char(
        string='Responsable factura electrónica'
    )

    fe_correo_electronico = fields.Char(
        string='Correo factura electrónica'
    )

    fe_sucursal = fields.Many2one(
        'res.partner',
        string='Sucursal'
    )

    company_partner_id = fields.Many2one(
        'res.partner',
        compute='compute_company_partner_id',
        string='Partner ID'
    )

    mostrar_sucursal = fields.Boolean(
        compute='compute_mostrar_sucursal',
        string='Mostrar Sucursales'
    )

    journal_id_fv = fields.Many2one(
        'account.journal',
        string='Diario FV - NC',
        states={'draft': [('readonly', False)]}
    )
    journal_id_nd = fields.Many2one(
        'account.journal',
        string='Diario ND',
        states={'draft': [('readonly', False)]}
    )
    fe_habilitada_compania = fields.Boolean(
        string='FE Compañía',
        compute='compute_fe_habilitada_compania',
        store=False,
        copy=False
    )
    postal_id = fields.Many2one('l10n_co_postal.postal_code', string="Código Postal", default=1)

    fe_facturador = fields.Boolean(
        string='Nombre Facturador',
        default=True
    )

    @api.onchange('company_partner_id')
    def compute_mostrar_sucursal(self):
        for partner in self:
            if partner.parent_id.id == partner.company_partner_id.id:
                partner.mostrar_sucursal = True
            else:
                partner.mostrar_sucursal = False

    @api.onchange('user_id')
    def compute_fe_habilitada_compania(self):
        for record in self:
            record.fe_habilitada_compania = self.env.company.fe_habilitar_facturacion

    @api.onchange('parent_id')
    def compute_company_partner_id(self):
        for partner in self:
            partner.company_partner_id = partner.env.user.company_id.partner_id

    @staticmethod
    def check_create_requirements(values):
        if values.get('fe_tipo_documento', False) == '31' and values.get('fe_digito_verificacion', False) == 'No aplica':
            raise ValidationError('Por favor seleccione el dígito de verificación correspondiente del NIT.')
        if values.get('fe_habilitada') and not validators.email(values.get('fe_correo_electronico')):
            raise ValidationError('El formato del correo electrónico es incorrecto.')

    def check_write_requirements(self):
        for record in self:
            if record.fe_tipo_documento == '31' and record.fe_digito_verificacion == 'No aplica':
                raise ValidationError('Por favor compruebe que el dígito de verificación sea correspondiente al NIT.')
            if record.fe_correo_electronico and not validators.email(record.fe_correo_electronico):
                raise ValidationError('El formato del correo electrónico es incorrecto.')

    @api.model
    def create(self, values):
        self.check_create_requirements(values)
        return super(ResPartner, self).create(values)

    def write(self, values):
        for record in self:
            partner = super(ResPartner, self).write(values)
            record.check_write_requirements()
            return partner

    @api.onchange('company_type')
    def update_person_type(self):
        for record in self:
            if record.company_type == 'company':
                record.fe_es_compania = '1'
                record.fe_primer_nombre = ''
                record.fe_segundo_nombre = ''
                record.fe_primer_apellido = ''
                record.fe_segundo_apellido = ''

            elif record.company_type == 'person':
                record.fe_es_compania = '2'
                record.fe_razon_social = ''

    @api.onchange('fe_es_contribuyente')
    def compute_gran_contribuyente(self):
        gran_contri = self.env['l10n_co_cei_settings.responsabilidad_fiscal'].search([('codigo_fe_dian','=','O-13')])
        for record in self:
            if record.fe_es_contribuyente:
                record.responsabilidad_fiscal_fe = [(4, gran_contri.id)]
            else:
                record.responsabilidad_fiscal_fe = [(3, gran_contri.id)]

    @api.onchange('responsabilidad_fiscal_fe')
    def compute_gran_contribuyente_check(self):
        gran_contri = self.env['l10n_co_cei_settings.responsabilidad_fiscal'].search([('codigo_fe_dian', '=', 'O-13')])
        for record in self:
            if gran_contri in record.responsabilidad_fiscal_fe:
                record.fe_es_contribuyente = True
            else:
                record.fe_es_contribuyente = False

    def find_or_create(self, email):
        """ Find a partner with the given ``email`` or use :py:method:`~.name_create`
            to create one

            :param str email: email-like string, which should contain at least one email,
                e.g. ``"Raoul Grosbedon <r.g@grosbedon.fr>"``"""
        assert email, 'an email is required for find_or_create to work'
        emails = tools.email_split(email)
        if emails:
            email = emails[0]
        ids = self.search([('fe_correo_electronico','=ilike',email)])
        if not ids:
            return super(ResPartner, self).find_or_create(email)
        return ids[0].id