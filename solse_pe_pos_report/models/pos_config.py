# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import api, fields, models, _

class PosConfig(models.Model):
	_inherit = 'pos.config'

	imp_reporte_cierre = fields.Boolean("Imprimir Reporte Cierre")
	tipo_rep_cierre = fields.Selection([("general", "Reporte General"), ("detallado", "Reporte Detallado")], default="general", string="Tipo Reporte Cierre")

	imp_reporte_actual = fields.Boolean("Imprimir Reporte Ventas Actual")
	tipo_rep_actual = fields.Selection([("general", "Reporte General"), ("detallado", "Reporte Detallado")], default="general", string="Tipo Reporte Cierre")