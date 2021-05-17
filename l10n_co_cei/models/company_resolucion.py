# -*- coding:utf-8 -*-
import datetime
from odoo import models, api, _, fields
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class company_resolucion(models.Model):
    _name = 'l10n_co_cei.company_resolucion'

    journal_id = fields.Many2one(
        'account.journal',
        string='Diario',
        ondelete='restrict',
        required=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        ondelete='restrict',
        required=True
    )
    name = fields.Char(
        string="Nombre de resolución",
        required=True
    )
    number = fields.Char(
        string="Número de resolución",
        required=True
    )
    rango_desde = fields.Integer(
        string='Rango desde',
        required=True
    )
    rango_hasta = fields.Integer(
        string='Rango hasta',
        required=True
    )
    fecha_inicial = fields.Date(
        string='Fecha inicial',
        required=True
    )
    fecha_final = fields.Date(
        string='Fecha final',
        required=True
    )
    prefijo = fields.Char(
        related='journal_id.sequence_id.prefix',
        string="Prefijo",
        store=False,
        readonly=True
    )
    prefijo_nota = fields.Char(
        related='journal_id.refund_sequence_id.prefix',
        string="Prefijo",
        store=False,
        readonly=True
    )
    consecutivo_envio = fields.Integer(
        string='Siguiente consecutivo de envío',
        required=True,
        default=1
    )
    clave_tecnica = fields.Char(
        string='Clave técnica',
    )
    tipo = fields.Selection(
        selection=[
            ('fisico', 'Físico'),
            ('por-computador', 'Por computador'),
            ('facturacion-electronica', 'Facturación electrónica')
        ],
        string='Tipo',
        required=True
    )
    state = fields.Selection(
        selection=[
            ('active', 'Activo'),
            ('inactive', 'Inactivo')
        ],
        string='Estado',
        default='active',
        required=True
    )

    categoria = fields.Selection(
        selection=[
            ('factura-venta', 'Facturas de venta'),
            ('nota-credito', 'Notas crédito'),
            ('nota-debito', 'Notas débito'),
            ('contingencia', 'Facturas de contingencia')
        ],
        string='Categoría',
        default='factura-venta',
        required=True
    )
    codigo_fe_dian = fields.Char(
        string='Código DIAN',
        compute='compute_codigos_dian'
    )

    category_resolution_dian_id = fields.Many2one(
        'l10n_co_cei.category_resolution',
        string='Tipo De Categoria de Resolución Dian'
    )

    fe_habilitada_compania = fields.Boolean(
        string='FE Compañía',
        compute='compute_fe_habilitada_compania',
        store=False,
        copy=False
    )

    @api.depends('codigo_fe_dian')
    def compute_fe_habilitada_compania(self):
        for record in self:
            if record.company_id:
                record.fe_habilitada_compania = record.company_id.fe_habilitar_facturacion
            else:
                record.fe_habilitada_compania = self.env.company.fe_habilitar_facturacion

    @api.depends('category_resolution_dian_id')
    def compute_codigos_dian(self):
        for resolution in self:
            resolution.codigo_fe_dian = ''
            if resolution.category_resolution_dian_id:
                resolution.codigo_fe_dian = resolution.category_resolution_dian_id.code

    _sql_constraints = [
        # (
        #     'resolucion_unique', 
        #     'unique(resolucion, fecha_inicial, company_id, journal_id)',
        #     'La relación entre compañia, journal, resolución y fecha inicial debe ser unica.'
        # ),
        (
            'rango_desde_entero_positivo_check',
            'check(rango_desde > 0)',
            'El consecutivo rango_desde debe ser un número entero positivo'
        ),
        (
            'rango_hasta_entero_positivo_check',
            'check(rango_hasta > 0)',
            'El consecutivo rango_hasta debe ser un número entero positivo'
        ),
        (
            'rango_desde_rango_hasta_check',
            'check(rango_desde < rango_hasta)',
            'El consecutivo rango_desde debe ser menor al consecutivo rango_hasta'
        ),
        # (
        #     'consecutivo_envio_check', 
        #     'check(consecutivo_envio >= minimo AND consecutivo <= rango_hasta)',
        #     'El consecutivo debe encontrarse dentro del rango especificado.'
        # ),
        (
            'fecha_inicial_fecha_final_check',
            'check(fecha_inicial < fecha_final)',
            'Fecha inicial debe ser menor a fecha final'
        )
    ]

    @api.constrains('company_id', 'journal_id', 'resolucion', 'fecha_inicial')
    def _check_unique_resolucion(self):
        for record in self:

            resolucion = self.env['l10n_co_cei.company_resolucion'].search([
                ('company_id', '=', record.company_id.id),
                ('journal_id', '=', record.journal_id.id),
                ('fecha_inicial', '=', record.fecha_inicial),
                ('state', '=', 'active'),
                ('id', '!=', record.id),
                ('categoria', '=', record.categoria)
            ],
                limit=1
            )

            if resolucion:
                raise ValidationError(
                    "Ya existe una resolución registrada con las características "
                    "especificadas"
                )

    def proximo_consecutivo(self):
        consecutivo_actual = self.consecutivo_envio
        self.consecutivo_envio += 1
        return str(consecutivo_actual)

    def _check_number(self):
        if self.categoria != 'nota-credito' or not self.journal_id.refund_sequence_id:
            number_next = self.journal_id.sequence_id.number_next
        else:
            number_next = self.journal_id.refund_sequence_id.number_next
        return (
                self.rango_desde <= number_next <= self.rango_hasta
        )

    def check_resolution(self):
        # validates if the next number of the sequence is within the
        # valid range
        return self._check_number()
