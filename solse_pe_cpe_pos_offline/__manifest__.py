# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

{
	'name': "SOLSE: Facturas offline",

	'summary': """
		Facturas offline
		""",

	'description': """
		Facturas offline
	""",

	'author': "F & M Solutions Service S.A.C",
	'website': "http://www.solse.pe",

	'category': 'Uncategorized',
	'version': '16.0.0.1',
	'license': 'Other proprietary',
	'depends': ['point_of_sale', 'solse_pe_cpe_pos'],

	'data': [
		'views/pos_config_view.xml',
	],
	'assets': {
		'point_of_sale.assets': [
			'solse_pe_cpe_pos_offline/static/src/css/pos.css',
			'solse_pe_cpe_pos_offline/static/src/js/screen.js',
			'solse_pe_cpe_pos_offline/static/src/js/PaymentScreen.js',
		],
	},
	'demo': [],
	'installable': True,
	'auto_install': False,
	'application': True,
	"sequence": 1,
}