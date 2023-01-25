odoo.define('solse_pe_pos_report.pos_screens', function(require) {
  "use strict";

var { Order } = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');
var utils = require('web.utils');
var round_pr = utils.round_precision;

const CPEReportOrder = (Order) => class CPEReportOrder extends Order {
	get_total_discount() {
		const ignored_product_ids = this._get_ignored_product_ids_total_discount()
		return round_pr(this.orderlines.reduce((sum, orderLine) => {
			if (!ignored_product_ids.includes(orderLine.product.id)) {
				sum += (orderLine.get_unit_price() * (orderLine.get_discount()/100) * orderLine.get_quantity());
				if (orderLine.display_discount_policy() === 'without_discount'){
					if (orderLine.get_lst_price() > 0) {
						sum += ((orderLine.get_lst_price() - orderLine.get_unit_price()) * orderLine.get_quantity());
					}
					//sum += ((orderLine.get_lst_price() - orderLine.get_unit_price()) * orderLine.get_quantity());
				}
			}
			return sum;
		}, 0), this.pos.currency.rounding);
	}
}
Registries.Model.extend(Order, CPEReportOrder);


});