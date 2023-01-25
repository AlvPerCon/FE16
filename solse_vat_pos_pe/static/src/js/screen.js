odoo.define('solse_vat_pos_pe.pos_screens', function(require) {
  "use strict";

	var { PosGlobalState } = require('point_of_sale.models');
	var PosDB = require('point_of_sale.DB');
	var core    = require('web.core');
	var rpc = require('web.rpc');
	var concurrency = require('web.concurrency');
	var QWeb = core.qweb;
	const Registries = require('point_of_sale.Registries');

	var _t = core._t;

	const PosModelVat = (PosGlobalState) => class PosModelVat extends PosGlobalState {
		constructor(obj, options) {
			super(...arguments);
			this.doc_types = [];
		}

		async _processData(loadedData) {
	        await super._processData(...arguments);
	        let identifications = loadedData['l10n_latam.identification.type'];
	        this.doc_code_by_id = {}
	        var self = this;
			_.each(identifications, function(doc) {
				self.doc_code_by_id[doc.id] = doc.l10n_pe_vat_code
			})
			this.doc_types = identifications
	    }
	}

	Registries.Model.extend(PosGlobalState, PosModelVat);

});