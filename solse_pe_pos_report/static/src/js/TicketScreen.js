odoo.define('solse_pe_pos_report.TicketScreen', function(require) {
    'use strict';

    const TicketScreen = require('point_of_sale.TicketScreen');
    const Registries = require('point_of_sale.Registries');
    const session = require('web.session');
    const TicketScreenReport = TicketScreen =>
        class extends TicketScreen {
        	getTable(order) {
                if(order.table) {
                	return `${order.table.floor.name} (${order.table.name})`;
                } else {
                	return "";
                }
            }

            getTipo(order) {
                return order.name;
            }
        }

    Registries.Component.extend(TicketScreen, TicketScreenReport);

    return TicketScreen;
})