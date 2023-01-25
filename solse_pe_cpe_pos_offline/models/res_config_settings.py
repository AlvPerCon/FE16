# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	factura_offline = fields.Many2one('l10n_latam.document.type', string="Documento de venta Offline", domain='[("sub_type", "=", "sale"), ("code", "=", "01")]',  readonly=False, related="pos_config_id.factura_offline")
	boleta_offline = fields.Many2one('l10n_latam.document.type', string="Documento de venta Offline", domain='[("sub_type", "=", "sale"),("code", "=", "03")]',  readonly=False, related="pos_config_id.boleta_offline")
	otro_offline = fields.Many2one('l10n_latam.document.type', string="Documento de venta Offline", domain='[("sub_type", "=", "sale"),("code", "not in", ["01", "03", "08", "07"])]',  readonly=False, related="pos_config_id.otro_offline")

	ult_numero_factura = fields.Integer("Ult número de factura", default=0, readonly=False, related="pos_config_id.ult_numero_factura")
	ult_numero_boleta = fields.Integer("Ult número de boleta", default=0,  readonly=False, related="pos_config_id.ult_numero_boleta")
	ult_numero_otro = fields.Integer("Ult número de otro", default=0,  readonly=False, related="pos_config_id.ult_numero_otro")
