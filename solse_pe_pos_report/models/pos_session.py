# -*- coding: utf-8 -*-
# Copyright (c) 2019-2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import models, fields, api
import logging
_logging = logging.getLogger(__name__)

class PosSession(models.Model):
	_inherit = 'pos.session'

	pago_ids = fields.One2many("pos.payment", "session_id", "Pagos")

	def imprimir_reporte_detallado(self):
		datos = {'tipo': 'detallado', 'id_session': self.id}
		self.recalcular_alto_reporte(datos)
		#solse_pe_pos_report.action_report_pos_momento_detallado_sesion
		return {
			'type': 'ir.actions.report',
			'report_name': "solse_pe_pos_report.report_momento_sesion_detallado",
			'report_file': "solse_pe_pos_report.report_momento_sesion_detallado",
			'report_type': 'qweb-pdf',
		}

	@api.model
	def recalcular_alto_reporte(self, vals):
		id_session = vals.get('id_session', False)
		tipo = vals.get('tipo', 'general')
		if not id_session:
			_logging.info("no se recibio id de sesion")
			return
		sesion = self.env['pos.session'].search([("id", "=", id_session)], limit=1)
		if not sesion:
			_logging.info("no se encontro una session con este id")
			return

		cant_filas_fijas = 16
		cant_saltos_lineas = 2
		cant_filas_dinamicas = len(sesion.obtener_resumen_cierre())
		cant_filas_dinamicas = cant_filas_dinamicas +  len(sesion.obtener_devoluciones_cierre())
		cant_filas_dinamicas = cant_filas_dinamicas +  len(sesion.obtener_ingresos_salidas())
		alto_adicional = 15
		alto_promedio_fila_dinamica = 5
		alto_promedio_fila_fijo = 6
		
		alto_dinamico = 0
		if tipo == 'detallado':
			cant_filas_fijas = cant_filas_fijas + 8
			alto_ventas = sesion.obtener_alto_ventas(alto_promedio_fila_dinamica)
			alto_devoluciones = sesion.obtener_atlo_detalle_devoluciones(alto_promedio_fila_dinamica)
			alto_ingresos_salidas = sesion.obtener_alto_ingresos_salidas_detalle(alto_promedio_fila_dinamica)
			alto_dinamico = alto_ventas + alto_devoluciones + alto_ingresos_salidas

		alto_total = alto_adicional + round(alto_promedio_fila_fijo * cant_filas_fijas) + round(alto_promedio_fila_dinamica * cant_filas_dinamicas)
		alto_total = alto_total + alto_dinamico

		paperformat_id = self.env.ref('solse_pe_pos_report.paperformat_ticket_cierre')
		cambio = paperformat_id.write({
			'page_height': alto_total
		})

	def obtener_alto_ventas(self, alto_x_linea):
		alto = 0
		for pedido in self.order_ids:
			if pedido.amount_total <= 0:
				continue
			datos = self.obtener_datos_pedido_reg(pedido)
			alto_tipo_comp = len(datos["tipo_comprobante"])
			alto_nro_comp = len(self.obtener_serie_correlativo(datos["numero"]))
			alto_tipo_pago = len(datos["tipo_pago"])
			alto_mayor = 0
			altos = [alto_tipo_comp, alto_nro_comp, alto_tipo_pago]
			for indice in range(0, len(altos)):
				if altos[indice] > alto_mayor:
					alto_mayor = altos[indice]

			cant_lineas_f = alto_mayor / 8
			cant_lineas = int(cant_lineas_f)
			if cant_lineas_f > cant_lineas:
				cant_lineas = cant_lineas + 1

			alto = alto + (alto_x_linea * cant_lineas)

		return alto

	def obtener_atlo_detalle_devoluciones(self, alto_x_linea):
		self.ensure_one()
		#domain_devoluciones = [('session_id', '=', self.id), ('amount', '<=', 0), ('payment_method_id.journal_id', '!=', False)]
		domain_devoluciones = [('session_id', '=', self.id), ('amount', '<=', 0)]
		result = self.env['pos.payment'].search(domain_devoluciones)
		alto = 0
		for reg in result:
			orden = reg.pos_order_id
			factura = orden.account_move
			if factura:
				datos = {
					"name": reg.name,
					"tipo_comprobante": factura.l10n_latam_document_type_id.name,
					"numero": self.obtener_serie_correlativo(factura.l10n_latam_document_number),
					"referencia": self.obtener_serie_correlativo(factura.origin_doc_id.l10n_latam_document_number),
					"amount": reg.amount
				}
			else:
				datos = {
					"name": reg.name,
					"tipo_comprobante": "",
					"numero": self.obtener_serie_correlativo(orden.number),
					"referencia": self.obtener_serie_correlativo(orden.refunded_order_ids[0].name if orden.refunded_order_ids else "No encontrado"),
					"amount": reg.amount
				}

			letra_tipo_comp = len(datos["tipo_comprobante"])
			letras_nro_comp = len(datos["numero"])
			letras_referencia = len(datos["referencia"])
			mayor_cant_letras = 0
			array_cant_letras = [letra_tipo_comp, letras_nro_comp, letras_referencia]
			for indice in range(0, len(array_cant_letras)):
				if array_cant_letras[indice] > mayor_cant_letras:
					mayor_cant_letras = array_cant_letras[indice]

			cant_lineas_f = mayor_cant_letras / 8
			cant_lineas = int(cant_lineas_f)
			if cant_lineas_f > cant_lineas:
				cant_lineas = cant_lineas + 1

			alto = alto + (alto_x_linea * cant_lineas)

		return alto

	def obtener_alto_ingresos_salidas_detalle(self, alto_x_linea):
		self.ensure_one()
		cash_in_count = 0
		cash_out_count = 0
		alto = 0
		for cash_move in self.statement_line_ids.sorted('create_date'):
			if cash_move.amount > 0:
				cash_in_count += 1
				name = f'Cash in {cash_in_count}'
			else:
				cash_out_count += 1
				name = f'Cash out {cash_out_count}'
			datos = {
				'name': cash_move.payment_ref if cash_move.payment_ref else name,
				'amount': cash_move.amount
			}

			letra_nombre = len(datos["name"])
			letras_monto = len(str(datos["amount"]))
			mayor_cant_letras = letra_nombre if letra_nombre > letras_monto else letras_monto

			cant_lineas_f = mayor_cant_letras / 8
			cant_lineas = int(cant_lineas_f)
			if cant_lineas_f > cant_lineas:
				cant_lineas = cant_lineas + 1

			alto = alto + (alto_x_linea * cant_lineas)

		return alto

	def obtener_resumen_cierre(self):
		self.ensure_one()
		result_casch = self.env['pos.payment'].read_group([('session_id', '=', self.id), ('payment_method_id.journal_id', '!=', False), ('amount', '>', 0), ('type', '=', 'cash')], ['amount'], ['payment_method_id'])
		result = self.env['pos.payment'].read_group([('session_id', '=', self.id), ('payment_method_id.journal_id', '!=', False), ('amount', '>', 0)], ['amount'], ['payment_method_id'])
		result_change = self.env['pos.payment'].read_group([('session_id', '=', self.id), ('is_change', '=', True)], ['amount'], ['payment_method_id'])
		#result = self.env['pos.payment'].read_group([('session_id', '=', self.id), '|', ('amount', '>', 0), ('is_change', '=', True)], ['amount'], ['payment_method_id'])

		respuesta_cash = {}
		for reg in result_casch:
			reg_pago = reg["payment_method_id"]
			reg_temp = reg_pago[1]
			respuesta_cash[reg_temp] = reg["amount"]

		respuesta_change = {}
		for reg in result_change:
			reg_pago = reg["payment_method_id"]
			reg_temp = reg_pago[1]
			respuesta_change[reg_temp] = reg["amount"]


		respuesta = []
		for reg in result:
			reg_pago = reg["payment_method_id"]
			reg_temp = reg_pago[1]
			monto_efectivo = 0
			monto_vuelto = 0
			if reg_temp in respuesta_cash:
				monto_efectivo = respuesta_cash[reg_temp]

			if reg_temp in respuesta_change:
				monto_vuelto = abs(respuesta_change[reg_temp])

			tipo = 'otro'
			if monto_efectivo > 0:
				tipo = 'efectivo'
			respuesta.append({
				"name": reg_temp,
				"amount": reg["amount"] - monto_vuelto,
				"type": tipo,
				"monto_efectivo": monto_efectivo - monto_vuelto,
			})

		return respuesta

	def obtener_datos_pedido(self, order_id):
		orden = self.env['pos.order'].search([("id", "=", order_id)], limit=1)
		factura = orden.account_move

		nombre_pago = ''
		for pago in orden.payment_ids:
			#pago = orden.payment_ids[indice]
			if nombre_pago == '':
				nombre_pago = pago.payment_method_id.name
			else:
				nombre_pago = nombre_pago + ", "+ pago.payment_method_id.name

		if factura:
			datos_rpt = {
				"tipo_comprobante": factura.l10n_latam_document_type_id.name,
				"numero": orden.number,
				"tipo_pago": nombre_pago,
			}
		else:
			datos_rpt = {
				"tipo_comprobante": "",
				"numero": orden.name,
				"tipo_pago": nombre_pago,
			}
		return datos_rpt

	def obtener_datos_pedido_reg(self, orden):
		factura = orden.account_move
		#pago = orden.payment_ids[0]
		nombre_pago = ''
		for pago in orden.payment_ids:
			#pago = orden.payment_ids[indice]
			if nombre_pago == '':
				nombre_pago = pago.payment_method_id.name
			else:
				nombre_pago = nombre_pago + ", "+ pago.payment_method_id.name

		if factura:
			datos_rpt = {
				"tipo_comprobante": factura.l10n_latam_document_type_id.name,
				"numero": orden.number,
				"tipo_pago": nombre_pago,
			}
		else:
			datos_rpt = {
				"tipo_comprobante": "",
				"numero": orden.name,
				"tipo_pago": nombre_pago,
			}
		return datos_rpt

	def obtener_serie_correlativo(self, numero):
		if not numero:
			return ""
		datos_array = numero.split("-")
		if len(datos_array) > 1:
			correlativo = str(datos_array[1])
			if correlativo.isdigit():
				entero = int(correlativo)
				return "%s-%s" % (datos_array[0], str(entero))
			else:
				return numero
		else:
			return numero

	def obtener_devoluciones_cierre(self):
		self.ensure_one()
		#domain_devoluciones = [('session_id', '=', self.id), ('amount', '<=', 0), ('payment_method_id.journal_id', '!=', False), ('is_change', '=', False)]
		#domain_devoluciones = [('session_id', '=', self.id), ('amount', '<=', 0), ('is_change', '=', False)]
		#result = self.env['pos.payment'].search(domain_devoluciones)
		domain_devoluciones = [('session_id', '=', self.id), ('amount_total', '<=', 0)]
		result = self.env['pos.order'].search(domain_devoluciones)
		respuesta = []
		json_diarios = {}
		json_efectivo = {}
		for orden in result:
			#orden = reg.pos_order_id
			factura = orden.account_move
			monto_devuelto_efectivo = 0
			for pago in orden.payment_ids:

				if pago.payment_method_id.type == 'cash':
					monto_devuelto_efectivo = monto_devuelto_efectivo + pago.amount

			if factura:
				
				if not factura.l10n_latam_document_type_id.name in json_diarios:
					json_diarios[factura.l10n_latam_document_type_id.name] = orden.amount_total
					json_efectivo[factura.l10n_latam_document_type_id.name] = monto_devuelto_efectivo
				else:
					json_diarios[factura.l10n_latam_document_type_id.name] = json_diarios[factura.l10n_latam_document_type_id.name] + orden.amount_total
					json_efectivo[factura.l10n_latam_document_type_id.name] = json_efectivo[factura.l10n_latam_document_type_id.name] + monto_devuelto_efectivo
			else:
				#pago = orden.payment_ids[0]
				for pago in orden.payment_ids:
					#pago = orden.payment_ids[indice]
					if not pago.payment_method_id.name in json_diarios:
						json_diarios[pago.payment_method_id.name] = pago.amount
						json_efectivo[pago.payment_method_id.name] = monto_devuelto_efectivo
					else:
						json_diarios[pago.payment_method_id.name] = json_diarios[pago.payment_method_id.name] + pago.amount
						json_efectivo[pago.payment_method_id.name] = json_efectivo[pago.payment_method_id.name] + monto_devuelto_efectivo
	

		for key in json_diarios:
			respuesta.append({
				"name": key,
				"amount": json_diarios[key],
				"monto_efectivo": abs(json_efectivo[key])
			})

		return respuesta

	def obtener_detalle_devoluciones(self):
		self.ensure_one()
		#domain_devoluciones = [('session_id', '=', self.id), ('amount', '<=', 0), ('payment_method_id.journal_id', '!=', False), ('is_change', '=', False)]
		domain_devoluciones = [('session_id', '=', self.id), ('amount_total', '<=', 0)]
		result = self.env['pos.order'].search(domain_devoluciones)
		respuesta = []
		for orden in result:
			factura = orden.account_move
			if factura:
				respuesta.append({
					"name": orden.name,
					"tipo_comprobante": factura.l10n_latam_document_type_id.name,
					"numero": factura.l10n_latam_document_number,
					"referencia": factura.origin_doc_id.l10n_latam_document_number,
					"amount": orden.amount_total
				})
			else:
				respuesta.append({
					"name": orden.name,
					"tipo_comprobante": "",
					"numero": orden.number,
					"referencia": orden.refunded_order_ids[0].name if orden.refunded_order_ids else "No encontrado",
					"amount": orden.amount_total
				})

		return respuesta

	def obtener_ingresos_salidas(self):
		self.ensure_one()
		orders = self.order_ids.filtered(lambda o: o.state == 'paid' or o.state == 'invoiced')
		payments = orders.payment_ids.filtered(lambda p: p.payment_method_id.type != "pay_later")
		pay_later_payments = orders.payment_ids - payments
		cash_payment_method_ids = self.payment_method_ids.filtered(lambda pm: pm.type == 'cash')
		default_cash_payment_method_id = cash_payment_method_ids[0] if cash_payment_method_ids else None
		total_default_cash_payment_amount = sum(payments.filtered(lambda p: p.payment_method_id == default_cash_payment_method_id).mapped('amount')) if default_cash_payment_method_id else 0
		other_payment_method_ids = self.payment_method_ids - default_cash_payment_method_id if default_cash_payment_method_id else self.payment_method_ids
		cash_in_count = 0
		cash_out_count = 0
		cash_in_out_list = []
		ingresos = 0
		salidas = 0
		for cash_move in self.statement_line_ids.sorted('create_date'):
			if cash_move.amount > 0:
				cash_in_count += 1
				name = f'Cash in {cash_in_count}'
				ingresos = ingresos + cash_move.amount
			else:
				cash_out_count += 1
				name = f'Cash out {cash_out_count}'
				salidas = salidas + cash_move.amount

		cash_in_out_list.append({
			'name': "Ingresos",
			'amount': ingresos
		})
		cash_in_out_list.append({
			'name': "Salidas",
			'amount': salidas
		})

		return cash_in_out_list

	def obtener_ingresos_salidas_detalle(self):
		self.ensure_one()
		orders = self.order_ids.filtered(lambda o: o.state == 'paid' or o.state == 'invoiced')
		payments = orders.payment_ids.filtered(lambda p: p.payment_method_id.type != "pay_later")
		pay_later_payments = orders.payment_ids - payments
		cash_payment_method_ids = self.payment_method_ids.filtered(lambda pm: pm.type == 'cash')
		default_cash_payment_method_id = cash_payment_method_ids[0] if cash_payment_method_ids else None
		total_default_cash_payment_amount = sum(payments.filtered(lambda p: p.payment_method_id == default_cash_payment_method_id).mapped('amount')) if default_cash_payment_method_id else 0
		other_payment_method_ids = self.payment_method_ids - default_cash_payment_method_id if default_cash_payment_method_id else self.payment_method_ids
		cash_in_count = 0
		cash_out_count = 0
		cash_in_out_list = []
		for cash_move in self.statement_line_ids.sorted('create_date'):
			if cash_move.amount > 0:
				cash_in_count += 1
				name = f'Cash in {cash_in_count}'
			else:
				cash_out_count += 1
				name = f'Cash out {cash_out_count}'
			cash_in_out_list.append({
				'name': cash_move.payment_ref if cash_move.payment_ref else name,
				'amount': cash_move.amount
			})

		return cash_in_out_list

