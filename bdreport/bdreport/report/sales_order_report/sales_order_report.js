// Copyright (c) 2016, vincent nguyen and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Order Report"] = {
	"filters": [
		{
			"fieldname":"period",
			"label": __("Period"),
			"fieldtype": "Select",
			options: [
				{ "value": "Month", "label": __("Month") },
				{ "value": "Quarter", "label": __("Quarter") }
			],
			"default": "Month",
			"width": "80",
			"on_change": function(query_report) {
				//check == Quarter
				var period = query_report.get_values().period;
				var period_num = query_report.get_values().period_num;
				if (period=='Quarter' && period_num>5) {
					frappe.query_report_filters_by_name.period_num.set_input(4);
				}
				query_report.trigger_refresh();
			}
		},
		{
			"fieldname":"period_num",
			"label": __("Period Num"),
			"fieldtype": "Select",
			"options": "1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12",
			"default": new Date().getMonth()+1,
			"width": "80",
			"on_change": function(query_report) {
				//check == Quarter
				var period = query_report.get_values().period;
				var period_num = query_report.get_values().period_num;
				if (period=='Quarter' && period_num>5) {
					frappe.query_report_filters_by_name.period_num.set_input(4);
				}
				query_report.trigger_refresh();
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
			"fieldname":"company",
			"label": "Company",
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.sys_defaults.company
		}
	]
}
