# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

{
	'name': "Búsqueda RUC/DNI desde POS",

	'summary': """
		Obtener datos con RUC o DNI desde POS
		""",

	'description': """
		Obtener los datos por RUC o DNI desde POS
	""",

	'author': "F & M Solutions Service S.A.C",
	'website': "http://www.solse.pe",

	'category': 'Uncategorized',
	'version': '16.0.0.2',
	'license': 'Other proprietary',
	'depends': ['point_of_sale', 'sale_management', 'pos_sale', 'l10n_pe', 'l10n_latam_base','solse_vat_pe'],

	'data': [
		'data/res_city_data.xml',
	],
	'assets': {
		'point_of_sale.assets': [
			'solse_vat_pos_pe/static/src/css/pos.css',
			'solse_vat_pos_pe/static/src/js/screen.js',
			'solse_vat_pos_pe/static/src/js/ClientDetailsEdit.js',
			'solse_vat_pos_pe/static/src/xml/**/*',
		],
	},
	'demo': [],
	'installable': True,
	'auto_install': False,
	'application': True,
	"sequence": 1,
}