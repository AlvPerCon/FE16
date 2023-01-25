var ejecutando = false;
odoo.define('solse_pe_cpe_pos_offline.PaymentScreen', function(require) {
	'use strict';

	const PaymentScreen = require('point_of_sale.PaymentScreen');
	const Registries = require('point_of_sale.Registries');
	const session = require('web.session');
	const core = require('web.core');
	const rpc = require('web.rpc');
	const NumberBuffer = require('point_of_sale.NumberBuffer');
	const { isConnectionError } = require('point_of_sale.utils');
	const _t = core._t;
	const QWeb = core.qweb;
	const { onMounted } = owl;

	const PaymentScreenOffline = PaymentScreen =>
		class extends PaymentScreen {

			

			validarSerieOffline() {
				let serie = "";
				//serie = "F002-545454";
				let tipo_doc_venta = this.currentOrder.get_cpe_type()
				let documento_offline = false;
				let ultimo_numero = 0;
				if(tipo_doc_venta == '01') {
					let rpt = this.currentOrder.obtenerSerieFactura()
					documento_offline  = rpt[0]
					ultimo_numero  = rpt[1]
				} else if(tipo_doc_venta == '03') {
					let rpt = this.currentOrder.obtenerSerieBoleta()
					documento_offline  = rpt[0]
					ultimo_numero  = rpt[1]
				} else {
					let rpt = this.currentOrder.obtenerSerieOtro()
					documento_offline  = rpt[0]
					ultimo_numero  = rpt[1]
				}

				if(!documento_offline) {
					return "";
				}
				//serie = "F050-00000458"
				let nro = ultimo_numero + 1
				let nro_texto = this.currentOrder.formatearCorrelativo(nro)
				serie = documento_offline.prefijo+"-"+nro_texto+""
				this.currentOrder.documento_offline = documento_offline.id
				this.currentOrder.l10n_latam_document_type_id = documento_offline.id
				this.currentOrder.number = serie
				this.currentOrder.numero_offline = serie
				//this.currentOrder.set_numero_offline(serie)

				if(tipo_doc_venta == '01') {
					this.currentOrder.actualizarSerieFactura(nro)
				} else if(tipo_doc_venta == '03') {
					this.currentOrder.actualizarSerieBoleta(nro)
				} else {
					this.currentOrder.actualizarSerieOtro(nro)
				}
				
				return serie;
			}

			

		};

	Registries.Component.extend(PaymentScreen, PaymentScreenOffline);

	return PaymentScreen;
});
