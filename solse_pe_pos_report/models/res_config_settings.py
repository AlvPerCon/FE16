# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	imp_reporte_cierre = fields.Boolean("Imprimir Reporte Cierre", related="pos_config_id.imp_reporte_cierre", readonly=False)
	tipo_rep_cierre = fields.Selection([("general", "Reporte General"), ("detallado", "Reporte Detallado")], string="Tipo Reporte Cierre", related="pos_config_id.tipo_rep_cierre", readonly=False)

	imp_reporte_actual = fields.Boolean("Imprimir Reporte Ventas Actual", related="pos_config_id.imp_reporte_actual", readonly=False)
	tipo_rep_actual = fields.Selection([("general", "Reporte General"), ("detallado", "Reporte Detallado")], string="Tipo Reporte Cierre", related="pos_config_id.tipo_rep_actual", readonly=False)


class PosPayment(models.Model):
	_inherit = 'pos.payment'

	type = fields.Selection(related="payment_method_id.type", store=True)