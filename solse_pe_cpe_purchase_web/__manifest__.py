# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

{
	'name': "Portal Proveedores: XML, PDF",

	'summary': """
		Portal Proveedores: XML, PDF""",

	'description': """
		Portal Proveedores: XML, PDF
	""",

	'author': "F & M Solutions Service S.A.C",
	'website': "https://www.solse.pe",
	'category': 'Website',
	'version': '16.0.0.1',
	'license': 'Other proprietary',
	'depends': [
		'base',
		'account',
		'web',
		'mail',
		'portal',
	],
	'data': [
		'views/account_move_view.xml',
	],
	'installable': True,
	'price': 70,
	'currency': 'USD',
}