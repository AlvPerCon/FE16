odoo.define('solse_pe_cpe_pos_offline.pos_screens', function(require) {
  "use strict";

	var { PosGlobalState, Order } = require('point_of_sale.models');
	var PosDB = require('point_of_sale.DB');
	var core    = require('web.core');
	var rpc = require('web.rpc');
	var concurrency = require('web.concurrency');
	var QWeb = core.qweb;
	const Registries = require('point_of_sale.Registries');

	var _t = core._t;
	const PosModelOffline = (PosGlobalState) => class PosModelOffline extends PosGlobalState {

		async _processData(loadedData) {
			await super._processData(...arguments);
			let documentos_venta = loadedData['l10n_latam.document.type'];
			this.l10n_latam_document_type_ids_todos = documentos_venta;
			var self = this;
			let nuevo = []
			for(let indice in documentos_venta) {
				let registro = documentos_venta[indice];
				let condicion1 = (registro.id == self.config.factura_offline[0]);
				let condicion2 = (registro.id == self.config.boleta_offline[0]);
				let condicion3 = (registro.id == self.config.otro_offline[0]);
				if(condicion1 || condicion2 || condicion3) {
					continue;
				}
				nuevo.push(registro)
			}

			this.l10n_latam_document_type_ids = nuevo;
			
			setTimeout(function(){
				self.cargarDatosOffline();
			}, 1500);
		}

		get_doc_type_sale_id(journal_id) {
			let doc_types = this.l10n_latam_document_type_ids_todos;
			if (!doc_types instanceof Array) {
				doc_types = [doc_types];
			}
			for (var i = 0, len = doc_types.length; i < len; i++) {
				this.doc_type_sale_by_id[doc_types[i].id] = doc_types[i];
			}
			return this.doc_type_sale_by_id[journal_id];
		}


		cargarDatosOffline() {
			if(this.env.pos.config.factura_offline) {
				let documento_offline = this.get_doc_type_sale_id(this.env.pos.config.factura_offline[0]);
				this.env.pos.config.ult_numero_factura = documento_offline.sequence_number_next - 1
			}
			if(this.env.pos.config.boleta_offline) {
				let documento_offline = this.get_doc_type_sale_id(this.env.pos.config.boleta_offline[0]);
				this.env.pos.config.ult_numero_boleta = documento_offline.sequence_number_next - 1
			}
			if(this.env.pos.config.otro_offline) {
				let documento_offline = this.get_doc_type_sale_id(this.env.pos.config.otro_offline[0]);
				this.env.pos.config.ult_numero_otro = documento_offline.sequence_number_next - 1
			}
			console.log(this.env.pos.config)
		}
	}

	Registries.Model.extend(PosGlobalState, PosModelOffline);

	const OfflineOrder = (Order) => 
		class OfflineOrder extends Order {

			init_from_JSON(json) {
				const res = super.init_from_JSON(...arguments);
				var self = this;
				self.numero_offline = json.numero_offline || false;
			}
			export_as_JSON() {
				const res = super.export_as_JSON(...arguments);
				res['numero_offline'] = this.numero_offline;
				return res;
			}

			get_numero_offline() {
				return this.numero_offline;
			}

			set_numero_offline(numero_offline) {
				this.assert_editable();
				this.numero_offline = numero_offline;
			}

			obtenerSerieFactura() {
				let documento = false;
				if(this.pos.config.factura_offline) {
					console.log("this.pos.config.factura_offline")
					console.log(this.pos.config.factura_offline)
					documento = this.pos.get_doc_type_sale_id(this.pos.config.factura_offline[0]) 
				}
				return [documento, this.pos.config.ult_numero_factura];
			}
			obtenerSerieBoleta() {
				let documento = false;
				if(this.pos.config.boleta_offline) {
					console.log("this.pos.config.boleta_offline")
					console.log(this.pos.config.boleta_offline)
					documento = this.pos.get_doc_type_sale_id(this.pos.config.boleta_offline[0]) 	
				}
				return [documento, this.pos.config.ult_numero_boleta];
			}
			obtenerSerieOtro() {
				let documento = false;
				if(this.pos.config.otro_offline) {
					documento = this.pos.get_doc_type_sale_id(this.pos.config.otro_offline[0]) 
				}
				return [documento, this.pos.config.ult_numero_otro];
			}

			formatearCorrelativo(nro){
				let cant_ini = (""+nro+"").length
				if(cant_ini == 8) {
					return nro
				}

				for(let indice=0; indice<(8-cant_ini);indice++) {
					nro = "0"+nro;
				}
				return nro;
			}

			actualizarSerieFactura(nro) {
				this.pos.config.ult_numero_factura = nro
			}
			actualizarSerieBoleta(nro) {
				this.pos.config.ult_numero_boleta = nro;
			}
			actualizarSerieOtro(nro) {
				this.pos.config.ult_numero_otro = nro
			}

		};

	Registries.Model.extend(Order, OfflineOrder);

});