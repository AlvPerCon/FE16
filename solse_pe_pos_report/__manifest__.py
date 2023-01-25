# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

{
	'name': "Reportes para el POS",

	'summary': """
		Reportes para el POS""",

	'description': """
		Reportes para el POS
	""",

	'author': "F & M Solutions Service S.A.C",
	'website': "http://www.solse.pe",
	'category': 'Operations',
	'version': '16.0.0.4',
	'license': 'Other proprietary',
	'depends': [
		'solse_pe_edi',
		'solse_pe_cpe',
		'point_of_sale',
		'pos_sale',
		'solse_pe_cpe_pos',
		#'pos_restaurant',
	],
	'data': [
		'security/ir.model.access.csv',
		'views/report_cierre_sesion.xml', 
		'views/report_momento_sesion.xml',
		'views/pos_config_view.xml',
		'views/pos_session.xml',
	],
	'assets': {
		'point_of_sale.assets': [
			'solse_pe_pos_report/static/src/js/ReportButton.js',
			'solse_pe_pos_report/static/src/js/ClosePosPopup.js',
			'solse_pe_pos_report/static/src/js/screen.js',
			'solse_pe_pos_report/static/src/js/TicketScreen.js',
			'solse_pe_pos_report/static/src/xml/pos_report.xml',
			'solse_pe_pos_report/static/src/xml/ReportButton.xml',
		],
	},
	'installable': True,
	'price': 80,
	'currency': 'USD',
}