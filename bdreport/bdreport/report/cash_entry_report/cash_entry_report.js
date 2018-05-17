// Copyright (c) 2016, vincent nguyen and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Cash Entry Report"] = {
	"filters": [
		{
			"fieldname":"period",
			"label": __("Period"),
			"fieldtype": "Select",
			"reqd": 1,
			options: [
				{ "value": "Month", "label": __("Month") }
				
			],
			"default": "Month",
			"width": "80",
			"on_change": function(query_report) {
				//check == Quarter
				var period = query_report.get_values().period;
				var period_num = query_report.get_values().period_num;
				
				//query_report.trigger_refresh();
				query_report.refresh();
			}
		},
		{
			"fieldname":"period_num",
			"label": __("Period Num"),
			"fieldtype": "Select",
			"options": "1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12",
			"default": new Date().getMonth()+1,
			"width": "80",
			"reqd": 1,
			"on_change": function(query_report) {
				//check == Quarter
				var period = query_report.get_values().period;
				var period_num = query_report.get_values().period_num;
				
				//query_report.trigger_refresh();
				query_report.refresh();
			}
		},
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Data",
			"default": new Date().getFullYear(),
			"reqd": 1
		},
		{
			"fieldname":"account",
			"label": __("Account"),
			"fieldtype": "Select",
			"reqd": 1,
			"width": "200",
			"options": "11110000 - Tiền mặt: Việt Nam đồng - bd\n11120001 - Tiền mặt: Ngoai tệ: USD - bd\n11211000 - Tiền gởi Ngân hàng: Việt Nam đồng: VCB hoạt kỳ - bd\n11212000 - Tiền gởi Ngân hàng: Việt Nam đồng: VCB định kỳ - bd",
			"default": "11110000 - Tiền mặt: Việt Nam đồng - bd",
			"get_query": function() {
				var company = frappe.query_report_filters_by_name.company.get_value();
				return {
					"doctype": "Account",
					"filters": {
						"company": company,
					}
				}
			}
		},
		
		{
			
			"fieldname":"company",
			"label": "Company",
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": frappe.sys_defaults.company
		}
	]
}