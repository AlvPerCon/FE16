odoo.define('solse_pe_pos_report.ReportButton', function(require) {
	'use strict';

	const PosComponent = require('point_of_sale.PosComponent');
	const ProductScreen = require('point_of_sale.ProductScreen');
	const { useListener } = require("@web/core/utils/hooks");
	const Registries = require('point_of_sale.Registries');
	var rpc = require('web.rpc');

	class ReportButton extends PosComponent {
		setup() {
            super.setup();
            useListener('click', this._onClick);
        }

		async _onClick() {

			let id_session = this.env.pos.pos_session.id;
			var vals = {
                'id_session': id_session,
                'tipo': this.env.pos.config.tipo_rep_actual,
            }
			await rpc.query({
                model: 'pos.session',
                method: 'recalcular_alto_reporte',
                args: [vals],
            }).then(function (result) {
                
            });

			if(this.env.pos.config.imp_reporte_actual) { 
				let nombre_reporte = "solse_pe_pos_report.action_report_pos_momento_sesion"
				if(this.env.pos.config.tipo_rep_actual == "detallado") {
					nombre_reporte = "solse_pe_pos_report.action_report_pos_momento_detallado_sesion"
				}
				this.env.legacyActionManager.do_action(nombre_reporte, {
					additional_context: {
						active_ids: [id_session]
					},
				});
			}		
		}
	}
	ReportButton.template = 'solse_pe_pos_report.ReportButton';

	ProductScreen.addControlButton({
		component: ReportButton,
		condition: function () {
            return true;
        },
	});

	Registries.Component.add(ReportButton);

	return ReportButton;
});
