# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_round
from datetime import datetime
import pytz
import logging

tz = pytz.timezone('America/Lima')
_logging = logging.getLogger(__name__)

class PosOrder(models.Model):
	_inherit = "pos.order"

	documento_offline = fields.Many2one('l10n_latam.document.type', string="Documento Offline",)
	numero_offline = fields.Char("Número offline")

	@api.model
	def _order_fields(self, ui_order):
		res = super(PosOrder, self)._order_fields(ui_order)
		res['documento_offline'] = ui_order.get('documento_offline', False)
		res['numero_offline'] = ui_order.get('numero_offline', False)
		return res

	def _create_invoice(self, move_vals):
		res = super(PosOrder, self)._create_invoice(move_vals)
		res._compute_needed_terms()
		return res

	def _export_for_ui(self, order):
		res = super(PosOrder, self)._export_for_ui(order)
		res["documento_offline"] = order.documento_offline.id
		res["numero_offline"] = order.numero_offline
		if order.documento_offline:
			res["l10n_latam_document_type_id"] = order.documento_offline.id

		if order.numero_offline:
			res["name"] = order.numero_offline

		return res

	
	def _prepare_invoice_vals(self):
		res = super(PosOrder, self)._prepare_invoice_vals()
		doc_code_prefix = ""
		if self.documento_offline.id:
			res['l10n_latam_document_type_id'] = self.documento_offline.id
			doc_code_prefix = self.documento_offline.doc_code_prefix
		elif self.l10n_latam_document_type_id.id:
			res['l10n_latam_document_type_id'] = self.l10n_latam_document_type_id.id
			doc_code_prefix = self.l10n_latam_document_type_id.doc_code_prefix

		if self.numero_offline:
			res['name'] = "%s %s" % (doc_code_prefix, self.numero_offline)
			res['fue_offline'] = True
		return res