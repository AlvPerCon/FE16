# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import models
from itertools import groupby
from odoo.osv.expression import AND

class PosSession(models.Model):
	_inherit = 'pos.session'

	def _pos_ui_models_to_load(self):
		result = super()._pos_ui_models_to_load()
		result.append('l10n_latam.identification.type')
		return result

	def _loader_params_l10n_latam_identification_type(self):
		return {
			'search_params': {
				'domain': [('country_id.code', '=', 'PE')],
				'fields': ['name', 'id', 'l10n_pe_vat_code'],
				'order': 'sequence',
			},
		}

	def _loader_params_res_partner(self):
		res = super(PosSession, self)._loader_params_res_partner()
		res['search_params']['fields'].extend(["state_id", "city_id", "l10n_pe_district", "doc_type", "doc_number", 
	"commercial_name", "legal_name", "is_validate", "state", "condition", "l10n_latam_identification_type_id"])
		return res
		

	def _get_pos_ui_l10n_latam_identification_type(self, params):
		datos = self.env['l10n_latam.identification.type'].search_read(**params['search_params'])
		return datos
