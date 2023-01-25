# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

{
	'name': "Facturacion desde Tienda web",

	'summary': """
		Facturacion desde Tienda web""",

	'description': """
		Facturación electrónica - Perú 
		Facturacion desde Tienda web
	""",

	'author': "F & M Solutions Service S.A.C",
	'website': "http://www.solse.pe",
	'category': 'Website',
	'version': '16.0.0.2',
	'license': 'Other proprietary',
	'depends': [
		'website_sale',
		'solse_vat_pe',
	],
	'data': [
		'views/templates.xml',
		'views/sale_order.xml',
	],
	'assets': {
		'web.assets_frontend': [
			'solse_pe_cpe_web/static/src/js/website_sale.js',
		],
	},
	'installable': True,
	'price': 40,
	'currency': 'USD',
}