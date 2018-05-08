# Copyright (c) 2013, vincent nguyen and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _
from frappe.utils import get_first_day, get_last_day, add_to_date, nowdate, getdate, add_days, add_months

def execute(filters=None):
	if not filters: filters = {}

	#filters.from_date = get_first_day(filters["period_num"] + '-' + filters["year"])
	#filters.to_date = get_last_day(filters["period_num"] + '-' + filters["year"])

	if(filters.period=="Month"):
		#convert from_date
		filters.from_date = get_first_day(filters.period_num + '-' + filters.year)
		filters.to_date =  get_last_day(filters.period_num + '-' + filters.year)
		#frappe.msgprint(filters.from_date)
	
	if(filters.period=="Quarter"):
		#convert from_date
		period_num = "1"
		if(filters.period_num=="2"):
			period_num = "4"
		if(filters.period_num=="3"):
			period_num = "7"
		if(filters.period_num=="4"):
			period_num = "10"
			
		filters.from_date = get_first_day(period_num + '-' + filters.year)
		filters.to_date = add_months(filters.from_date, 3)
		filters.to_date = add_days(filters.to_date, -1)
		#frappe.msgprint(filters.from_date)


	address = frappe.get_doc("Address", filters.company)
	company = frappe.get_doc("Company", filters.company)

	data_to_be_printed = {
		"company": company,
		"address": address
	}

	columns = get_columns()
	data = get_invoices(filters)
	return columns, data, None, None, data_to_be_printed
	
def get_columns():
	columns = []
	return [
		"Date::100", "Id:Link/Quotation:100", "Customer Name::350",
		"Grand Total:Currency:150","Tax:Currency:150","Status::150"
	]
	return columns

def get_invoices(filters):
	conditions = get_conditions(filters)

	query = """SELECT so.transaction_date, so.name, so.customer_name, 
	so.base_grand_total, so.base_total_taxes_and_charges, so.status
	FROM `tabQuotation` so
	WHERE so.docstatus = 1 
	%s
	""" %(conditions)

	data = frappe.db.sql(query, as_list=1)

	return data
	

def get_conditions(filters):
	conditions = ""

	if filters.get("from_date"):
		conditions += " and so.transaction_date >= '%s'" % filters["from_date"]

	if filters.get("to_date"):
		conditions += " and so.transaction_date <= '%s'" % filters["to_date"]
	
	return conditions	
