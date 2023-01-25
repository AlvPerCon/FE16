# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

{
	'name': "Herramientas para CPE Sunat",

	'summary': """
		Herramientas para CPE Sunat
		""",

	'description': """
		Herramientas para tratar casos especiales con respecto a la facturación electrónica
	""",

	'author': "F & M Solutions Service S.A.C",
	'website': "https://www.solse.pe",

	'category': 'Uncategorized',
	'version': '16.0.0.1',
	'license': 'Other proprietary',
	'depends': ['base', 'l10n_pe', 'solse_pe_cpe'],

	'data': [
		'security/ir.model.access.csv',
		'wizard/agrupar_boletas_view.xml',
	],
	'demo': [],
	'installable': True,
	'auto_install': False,
	'application': True,
	"sequence": 1,
}