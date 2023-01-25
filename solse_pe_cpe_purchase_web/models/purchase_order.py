# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import models, fields, api
import base64
from odoo.exceptions import UserError, Warning
from xml.dom import minidom
import logging
_logging = logging.getLogger(__name__)

class IrAttachment(models.Model):
	_inherit = "ir.attachment"

	def _check_contents(self, values):
		mimetype = values['mimetype'] = self._compute_mimetype(values)
		xml_like = 'ht' in mimetype or ( # hta, html, xhtml, etc.
				'xml' in mimetype and    # other xml (svg, text/xml, etc)
				not 'openxmlformats' in mimetype)  # exception for Office formats
		user = self.env.context.get('binary_field_real_user', self.env.user)
		if not isinstance(user, self.pool['res.users']):
			raise UserError(_("binary_field_real_user should be a res.users record."))
		force_text = xml_like and (
			self.env.context.get('attachments_mime_plainxml') or
			not self.env['ir.ui.view'].with_user(user).check_access_rights('write', False))
		force_text = False
		if force_text:
			values['mimetype'] = 'text/plain'
		if not self.env.context.get('image_no_postprocess'):
			values = self._postprocess_contents(values)
		return values


class PurchaseOrder(models.Model):
	_inherit = "purchase.order"

	attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'purchase.order')], string='Archivos')

	def leer_archivos(self):
		if self.invoice_count:
			return
		if not self.order_line:
			raise UserError("La compra no cuenta con lineas facturables")
		for archivo in self.attachment_ids:
			tipo = archivo.mimetype
			if tipo:
				tipo = tipo.split("/")[1]
			else:
				continue

			if tipo not in ["xml"]:
				continue
			decoded_data = base64.b64decode(archivo.datas)
			dom = minidom.parseString(decoded_data)
			es_linea_valida = self.obtener_compra_json_de_xml(dom, archivo.datas, archivo.name)

	def obtener_pdf_para_xml(self, nombre_pdf):
		for archivo in self.attachment_ids:
			if archivo.name == nombre_pdf:
				return archivo.datas

		return False


	def obtener_compra_json_de_xml(self, xml_datos, archivo_binario, nombre_binario):
		if not xml_datos.getElementsByTagName("cac:Signature"):
			raise UserError("No se pudo encontrar la serie para el documento %s, revise que sea un xml valido y no un CDR" % nombre_binario)
		data_serie = xml_datos.getElementsByTagName("cac:Signature")[0].getElementsByTagName("cbc:ID")[0]
		serie_correlativo = data_serie.firstChild.data
		opciones_correlativo = xml_datos.getElementsByTagName("cbc:ID")
		for opcion in opciones_correlativo:
			serie_correlativo = opcion.firstChild.data
			if len(serie_correlativo.split("-")) > 1:
				break
		
		data_fecha = xml_datos.getElementsByTagName("cbc:IssueDate")[0]
		fecha_factura = data_fecha.firstChild.data

		data_fecha_vencimiento = xml_datos.getElementsByTagName("cbc:DueDate")
		fecha_vencimiento = False
		if data_fecha_vencimiento:
			fecha_vencimiento = data_fecha_vencimiento[0].firstChild.data
		else:
			data_fecha_vencimientos = xml_datos.getElementsByTagName("cbc:PaymentDueDate")
			for data_fecha_vencimiento in data_fecha_vencimientos:
				fecha_vencimiento = data_fecha_vencimiento.firstChild.data

		data_tipo_doc = xml_datos.getElementsByTagName("cbc:InvoiceTypeCode")[0]
		tipo_doc = data_tipo_doc.firstChild.data

		#data_monto_letras = xml_datos.getElementsByTagName("cbc:Note")[0]
		#monto_letras = data_monto_letras.firstChild.data

		data_moneda = xml_datos.getElementsByTagName("cbc:DocumentCurrencyCode")[0]
		moneda = data_moneda.firstChild.data

		# quien emite la factura
		"""nodo_proveedor = xml_datos.getElementsByTagName("cac:SignatoryParty")[0]
		ruc_proveedor = nodo_proveedor.getElementsByTagName("cbc:ID")[0].firstChild.data
		nombre_proveedor = nodo_proveedor.getElementsByTagName("cbc:Name")[0].firstChild.data"""

		nodo_proveedor = xml_datos.getElementsByTagName("cac:AccountingSupplierParty")[0]
		ruc_proveedor = nodo_proveedor.getElementsByTagName("cbc:ID")[0].firstChild.data
		if ruc_proveedor not in [self.partner_id.vat, self.partner_id.doc_number]:
			raise UserError("El ruc del proveedor no corresponde al de la orden de compra")

		nombre_proveedor = nodo_proveedor.getElementsByTagName("cbc:RegistrationName")[0].firstChild.data

		nodo_cliente = xml_datos.getElementsByTagName("cac:AccountingCustomerParty")[0]
		data_ruc = nodo_cliente.getElementsByTagName("cbc:ID")[0]
		cliente_tipo_doc = data_ruc.getAttribute("schemeID")
		data_cliente = nodo_cliente.getElementsByTagName("cbc:RegistrationName")[0]
		nombre_cliente = data_cliente.firstChild.data
		ruc_cliente = data_ruc.firstChild.data

		if ruc_cliente not in [self.company_id.partner_id.vat, self.company_id.partner_id.doc_number]:
			raise UserError("El cliente asignado en el xml no corresponde a esta empresa a la que le esta cargando el xml")

		#if self.company_id.vat != ruc_cliente:
		#	raise Warning("La factura "+serie_correlativo+" no corresponde a la empresa en curso, esta factura pertenece a la empresa "+nombre_cliente)

		nodo_termino_pago = xml_datos.getElementsByTagName("cac:PaymentTerms")[0]
		data_termino_pago_id = nodo_termino_pago.getElementsByTagName("cbc:ID")[0]
		data_termino_pago_nombre = nodo_termino_pago.getElementsByTagName("cbc:PaymentMeansID")[0]
		termino_pago_id = data_termino_pago_id.firstChild.data
		termino_pago_nombre = data_termino_pago_nombre.firstChild.data

		moneda_id = self.env["res.currency"].search([("name", "=", moneda)], limit=1)
		diario = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)

		tipo_documento = self.env["l10n_latam.document.type"].search([("code", "=", "01")], limit=1)
		entidad = self.obtener_entidad(cliente_tipo_doc, ruc_proveedor)

		factura_existe = self.env["account.move"].search([("move_type", "=", "in_invoice"), ("ref", "=", serie_correlativo), ("partner_id", "=", entidad.id)])
		if factura_existe:
			raise Warning("La factura "+serie_correlativo+" ya existe regitrada con el proveedor: "+entidad.display_name)

		
		nombre_pdf = nombre_binario.replace(".xml", ".pdf")
		pdf_binary = self.obtener_pdf_para_xml(nombre_pdf)
		datos_json = {
			"partner_id": entidad.id,
			'company_id': self.company_id.id,
			"invoice_date": fecha_factura,
			"move_type": "in_invoice",
			"journal_id": diario.id,
			"currency_id": moneda_id.id,
			"l10n_latam_document_type_id": tipo_documento.id,
			"ref": serie_correlativo,
			"data_xml": archivo_binario,
			"datas_fname": nombre_binario,
			"data_pdf": pdf_binary,
			"datas_fname_pdf": nombre_pdf,
			#"termino_pago_id": termino_pago_id,
			#"termino_pago_nombre": termino_pago_nombre,
		}
		if fecha_vencimiento:
			datos_json["invoice_date_due"] = fecha_vencimiento

		array_lineas = []
		lineas = xml_datos.getElementsByTagName("cac:InvoiceLine")
		compra = False
		for linea in lineas:
			data_cantidad = linea.getElementsByTagName("cbc:InvoicedQuantity")[0]
			tipo_unidad = data_cantidad.getAttribute("unitCode")
			cantidad = data_cantidad.firstChild.data
			data_precio = linea.getElementsByTagName("cac:Price")[0].getElementsByTagName("cbc:PriceAmount")[0]
			moneda = data_precio.getAttribute("currencyID")
			precio = data_precio.firstChild.data

			data_precio_ref = linea.getElementsByTagName("cac:PricingReference")[0]
			precio_ref = data_precio_ref.getElementsByTagName("cbc:PriceAmount")[0].firstChild.data

			data_producto = linea.getElementsByTagName("cac:Item")[0]
			data_item_producto = data_producto.getElementsByTagName("cbc:ID")
			id_producto = False
			if data_item_producto and data_item_producto[0].firstChild:
				id_producto = data_item_producto[0].firstChild.data
				
			nombre_producto = data_producto.getElementsByTagName("cbc:Description")[0].firstChild.data
			invoice_line_vals = {
				"name": nombre_producto,
				"quantity": cantidad,
				#"account_id": self.cuenta_lineas_factura.id,
				"price_unit": precio,
				"tax_ids": self.obtener_impuestos_compra(linea.getElementsByTagName("cac:TaxSubtotal"), precio_ref),
			}
			linea_compra = self.obtener_id_linea_compra(invoice_line_vals)
			compra = linea_compra.order_id
			invoice_line_vals['product_id'] = linea_compra.product_id.id
			invoice_line_vals['purchase_line_id'] = linea_compra.id
			array_lineas.append((0, 0, invoice_line_vals))

		datos_json["invoice_line_ids"] = array_lineas
		factura = self.env['account.move'].create(datos_json)
		for archivo in compra.attachment_ids:
			nuevo_reg = archivo.copy()
			nuevo_reg.write({'res_model': 'account.move', 'res_id': factura.id})

		factura.obtener_zip_archivos()
		return True

	def obtener_id_linea_compra(self, linea_factura):
		linea_compra = self.order_line.filtered(lambda x: x.product_qty == float(linea_factura['quantity']) and x.price_unit == float(linea_factura['price_unit']))
		if not linea_compra:
			linea_compra = self.order_line.filtered(lambda x: x.product_qty == float(linea_factura['quantity']))

		if not linea_compra:
			linea_compra = self.order_line[0]

		return linea_compra or False

	def obtener_entidad(self, tipo_documento, nro_ruc):
		dominio = ['|', ('vat', '=', nro_ruc), ('doc_number', '=', nro_ruc)]
		res_partner = self.env['res.partner'].search(dominio, limit=1)
		if res_partner:
			return res_partner
		else:
			raise Warning("No se pudo establecer el proveedor")


	def obtener_producto(self, id_producto, nombre_producto):
		obj_producto = self.env["product.product"]
		producto = obj_producto.search([("barcode", "=", id_producto)], limit=1)
		if producto:
			return producto

		producto = obj_producto.search([("default_code", "=", id_producto)], limit=1)
		if producto:
			return producto

		nombre = nombre_producto.replace("<![CDATA[", "")
		nombre = nombre.replace("]]", "")
		producto = obj_producto.search([("name", "=", nombre)], limit=1)

		if producto:
			return producto

		producto = obj_producto.search([], limit=1)
		return producto

	def obtener_impuestos_compra(self, data_impuestos, precio_ref):
		array_ids = []
		for data_impuesto in data_impuestos:
			impuesto_type_code = data_impuesto.getElementsByTagName("cbc:TaxTypeCode")[0].firstChild.data
			impuesto_code = data_impuesto.getElementsByTagName("cac:TaxScheme")[0].getElementsByTagName("cbc:ID")[0].firstChild.data
			impuesto = self.env["account.tax"].search([("type_tax_use", "=", "purchase"), ("l10n_pe_edi_tax_code", "=", impuesto_code), ("price_include", "=", False)], limit=1)
			if not impuesto:
				impuesto = self.env["account.tax"].search([("type_tax_use", "=", "purchase"), ("l10n_pe_edi_tax_code", "=", impuesto_code)], limit=1)
			if not impuesto:
				raise UserError('No se encontro registrado un impuesto para el codigo %s de tipo %s' % (impuesto_code, impuesto_type_code))
			array_ids.append(impuesto.id)

		return [(6, 0,array_ids)]




	