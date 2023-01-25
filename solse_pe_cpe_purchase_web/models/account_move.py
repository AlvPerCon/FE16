# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import models, fields, api
import base64
from odoo.exceptions import UserError, Warning
from xml.dom import minidom
import base64, zipfile
from io import StringIO, BytesIO
import os
import logging
_logging = logging.getLogger(__name__)

class ClaseFactura(models.Model):
	_inherit = "account.move"

	datas_fname = fields.Char("Nombre xml")
	data_xml = fields.Binary(string="XML")
	datas_fname_pdf = fields.Char("Nombre pdf")
	data_pdf = fields.Binary(string="PDF")

	datas_zip_fname = fields.Char("Nombre de archivo zip",  readonly=True)
	datas_zip = fields.Binary("Datos Zip", readonly=True)
	attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'account.move')], string='Archivos')

	def obtener_zip_archivos(self):
		in_memory_data = BytesIO()
		in_memory_zip = zipfile.ZipFile(in_memory_data, 'w', zipfile.ZIP_DEFLATED, False)

		for item in self.attachment_ids:
			filecontent = base64.b64decode(item.datas)
			in_memory_zip.writestr(item.name, filecontent)

		for zfile in in_memory_zip.filelist:
			zfile.create_system = 0
		in_memory_zip.close()

		self.datas_zip = base64.b64encode(in_memory_data.getvalue())
		self.datas_zip_fname = "%s.zip" % (self.ref or self.name)


	def descargar(self):
		# getting working module where your current python file (model.py) exists
		path = os.path.dirname(os.path.realpath(__file__)) 

		# creating dynamic path to create zip file
		nombre_archivo = self.name
		file_name = "../static/src/any_folder/"  + nombre_archivo
		file_name_zip = file_name+".rar"
		zipfilepath = os.path.join(path, file_name_zip)
		# creating zip file in above mentioned path
		zip_archive = zipfile.ZipFile(zipfilepath, "w", zipfile.ZIP_DEFLATED, False)

		# creating file name (like example.txt) in which we have to write binary field data or attachment
		object_name = self.datas_zip_fname 
		#object_handle = open(zipfilepath, "w")
		# writing binary data into file handle
		for item in self.attachment_ids:
			filecontent = base64.b64decode(item.datas)
			#zip_archive.writestr(item.name, filecontent)
			zip_archive.write(item.datas)
			#object_handle.write(str(base64.b64decode(item.datas))) 

		#object_handle.writestr(isBase64_decodestring(self.datas_zip)) 
		#object_handle.close()
		# writing file into zip file
		#zip_archive.write(object_name)
		zip_archive.close()

		# code snipet for downloading zip file
		return {
			'type': 'ir.actions.act_url',
			'url': str('/solse_pe_cpe_purchase_web/static/src/any_folder/'+str(nombre_archivo+".rar")),
			'target': 'new',
		}