# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import models, fields, _
from odoo.exceptions import UserError


class AgruparResumen(models.TransientModel):
	_name = "solse.agrupar.resumen"
	_description = "Agrupar boletas en resumen"

	force_post = fields.Boolean(string="Force", help="Las entradas en el futuro están configuradas para publicarse automáticamente de forma predeterminada. Marque esta casilla de verificación para publicarlos ahora.")

	def crear_resumen_cpe(self):
		comprobantes = self.env['solse.cpe'].browse(self._context.get('active_ids', []))
		for reg in comprobantes:
			if reg.estado_sunat not in ['01', '07', '09']:
				continue
			invoice_id = reg.invoice_ids[0]
			if not invoice_id:
				raise UserError('No se encontro un comprobante dentro de %s' % reg.name)
			
			if invoice_id.pe_invoice_code != '03':
				continue
			pe_summary_id = self.env['solse.cpe'].get_cpe_async('rc', invoice_id)
			invoice_id.pe_summary_id = pe_summary_id.id

		return {'type': 'ir.actions.act_window_close'}
