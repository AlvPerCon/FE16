# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models, _
from odoo.exceptions import UserError, Warning
import logging
import re
_logging = logging.getLogger(__name__)

 
class AccountMoveSerie(models.Model):
	_inherit = 'account.move'

	fue_offline = fields.Boolean("Fue offiline")

	@api.depends('posted_before', 'state', 'journal_id', 'date')
	def _compute_name(self):
		res = super(AccountMoveSerie, self)._compute_name()
		for move in self:
			if move.name not in ['/', '//', '/0'] and move.usar_prefijo_personalizado and move.state == 'posted' and move.fue_offline:
				sequence = move._get_sequence()
				numero = move.name.split("-")
				numero = int(numero[1])
				sequence.number_next = (numero + 1)
				move.procesar_cpe_offline()
		self._compute_split_sequence()


	def procesar_cpe_offline(self):
		if not self.pe_cpe_id:
			return

		if not self.pe_cpe_id.state == 'draft':
			return

		self.pe_cpe_id = self.pe_cpe_id.id
		self.pe_cpe_id.generate_cpe()
		if self.company_id.pe_is_sync:
			if self.l10n_latam_document_type_id.is_synchronous:
				self.pe_cpe_id.action_send()
		
		if (self.l10n_latam_document_type_id.code in ('07', '08') and self.origin_doc_code == '03' or self.l10n_latam_document_type_id.code == '03') and (not self.l10n_latam_document_type_id.is_synchronous):
			pe_summary_id = self.env['solse.cpe'].get_cpe_async('rc', self)
			self.pe_summary_id = pe_summary_id.id

		if self.company_id.enviar_email:
			self.enviarCorreoCPE()
