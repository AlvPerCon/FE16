odoo.define('solse_pe_pos_report.ClosePosPopup', function(require) {
	'use strict';

	const ClosePosPopup = require('point_of_sale.ClosePosPopup');
	const Registries = require('point_of_sale.Registries');
	const session = require('web.session');
	const core = require('web.core');
	const { identifyError } = require('point_of_sale.utils');
	const { ConnectionLostError, ConnectionAbortedError, RPCError } = require('@web/core/network/rpc_service');
	const _t = core._t;
	const rpc = require('web.rpc');
	const QWeb = core.qweb;

	const ClosePosPopupVat = ClosePosPopup =>
		class extends ClosePosPopup {
			constructor() {
				super(...arguments);
			}
			mounted() {
				super.mounted();
			}
			finalizar(){
				
			}
			
			async closeSession() {
				if (!this.closeSessionClicked) {
					this.closeSessionClicked = true;
					let response;
					if (this.cashControl) {
						 response = await this.rpc({
							model: 'pos.session',
							method: 'post_closing_cash_details',
							args: [this.env.pos.pos_session.id],
							kwargs: {
								counted_cash: this.state.payments[this.defaultCashDetails.id].counted,
							}
						})
						if (!response.successful) {
							return this.handleClosingError(response);
						}
					}
					await this.rpc({
						model: 'pos.session',
						method: 'update_closing_control_state_session',
						args: [this.env.pos.pos_session.id, this.state.notes]
					})
					try {
						const bankPaymentMethodDiffPairs = this.otherPaymentMethods
							.filter((pm) => pm.type == 'bank')
							.map((pm) => [pm.id, this.state.payments[pm.id].difference]);
						response = await this.rpc({
							model: 'pos.session',
							method: 'close_session_from_ui',
							args: [this.env.pos.pos_session.id, bankPaymentMethodDiffPairs],
						});
						if (!response.successful) {
							return this.handleClosingError(response);
						}
						var vals = {
							'id_session': this.env.pos.pos_session.id,
							'tipo': this.env.pos.config.tipo_rep_cierre,
						}
						var self = this
						if(this.env.pos.config.imp_reporte_cierre) { 
							await this.rpc({
								model: 'pos.session',
								method: 'recalcular_alto_reporte',
								args: [vals],
							});
							let id_session = this.env.pos.pos_session.id;
							let nombre_reporte = "solse_pe_pos_report.action_report_pos_cierre_sesion"
							if(this.env.pos.config.tipo_rep_cierre == "detallado") {
								nombre_reporte = "solse_pe_pos_report.action_report_pos_cierre_detallado_sesion"
							}
							await this.env.pos.do_action(nombre_reporte, {
								additional_context: {
									active_ids: [id_session],
								},
							});
							self.closeSessionClicked = false;
							setTimeout(function(){
								window.location = '/web#action=point_of_sale.action_client_pos_menu';
							}, 1000);
						} else {
							window.location = '/web#action=point_of_sale.action_client_pos_menu';
						}
					} catch (error) {
						const iError = identifyError(error);
						if (iError instanceof ConnectionLostError || iError instanceof ConnectionAbortedError) {
							await this.showPopup('ErrorPopup', {
								title: this.env._t('Network Error'),
								body: this.env._t('Cannot close the session when offline.'),
							});
						} else {
							await this.showPopup('ErrorPopup', {
								title: this.env._t('Closing session error'),
								body: this.env._t(
									'An error has occurred when trying to close the session.\n' +
									'You will be redirected to the back-end to manually close the session.')
							})
							window.location = '/web#action=point_of_sale.action_client_pos_menu';
						}
					}
					this.closeSessionClicked = false;
				}
			}

			async imprimirCierre() {
					
			}
		};

	Registries.Component.extend(ClosePosPopup, ClosePosPopupVat);

	return ClosePosPopup;
});
