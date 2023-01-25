# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import models
from itertools import groupby
from odoo.osv.expression import AND

class PosSession(models.Model):
	_inherit = 'pos.session'


	def _loader_params_l10n_latam_document_type(self):
		array_ids = self.config_id.documento_venta_ids.ids
		if self.config_id.factura_offline:
			array_ids.append(self.config_id.factura_offline.id)
		if self.config_id.boleta_offline:
			array_ids.append(self.config_id.boleta_offline.id)
		if self.config_id.otro_offline:
			array_ids.append(self.config_id.otro_offline.id)
		return {
			'search_params': {
				'domain': [('id', 'in', array_ids)],
				'fields': [],
			},
		}

	def _loader_params_pos_order(self):
		res = super(PosSession, self)._loader_params_pos_order()
		res['search_params']['fields'].extend(["documento_offline", "numero_offline"])
		return res
	