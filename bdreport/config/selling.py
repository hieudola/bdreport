from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Other Reports"),
			"icon": "fa fa-list",
			"items": [
				{
					"type": "report",
					"name": "Sales Order Report",
					"doctype": "Sales Order",
					"is_query_report": True,
				},
				{
					"type": "report",
					"name": "Sales Invoice Report",
					"doctype": "Sales Invoice",
					"is_query_report": True,
				}
			]

		}
    ]        