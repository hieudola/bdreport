from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, cstr, flt, get_first_day, get_last_day, add_to_date, nowdate, add_days, add_months
from frappe import _, _dict
from erpnext.accounts.utils import get_account_currency



def execute(filters=None):
	if not filters: filters = {}
	

	#filters.from_date = get_first_day(filters["period_num"] + '-' + filters["year"])
	#filters.to_date = get_last_day(filters["period_num"] + '-' + filters["year"])

	if(filters.period=="Month"):
		#convert from_date
		filters.from_date = get_first_day(filters.period_num + '-' + filters.year)
		filters.to_date =  get_last_day(filters.period_num + '-' + filters.year)
		#frappe.msgprint(filters.from_date)
			
	account_details = {}
	for acc in frappe.db.sql("""select name, is_group from tabAccount""", as_dict=1):
		account_details.setdefault(acc.name, acc)

	validate_filters(filters, account_details)

	validate_party(filters)

	filters = set_account_currency(filters)

	columns = get_columns(filters)

	res = get_result(filters, account_details)

	return columns, res

def validate_filters(filters, account_details):
	if not filters.get('company'):
		frappe.throw(_('{0} is mandatory').format(_('Company')))

	if filters.get("account") and not account_details.get(filters.account):
		frappe.throw(_("Account {0} does not exists").format(filters.account))

	if filters.get("account") and filters.get("group_by_account") \
			and account_details[filters.account].is_group == 0:
		frappe.throw(_("Can not filter based on Account, if grouped by Account"))

	if filters.get("voucher_no") and filters.get("group_by_voucher"):
		frappe.throw(_("Can not filter based on Voucher No, if grouped by Voucher"))

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))


def validate_party(filters):
	party_type, party = filters.get("party_type"), filters.get("party")

	if party:
		if not party_type:
			frappe.throw(_("To filter based on Party, select Party Type first"))
		elif not frappe.db.exists(party_type, party):
			frappe.throw(_("Invalid {0}: {1}").format(party_type, party))

def set_account_currency(filters):
	if not (filters.get("account") or filters.get("party")):
		return filters
	else:
		filters["company_currency"] = frappe.db.get_value("Company", filters.company, "default_currency")
		account_currency = None

		if filters.get("account"):
			account_currency = get_account_currency(filters.account)
		elif filters.get("party"):
			gle_currency = frappe.db.get_value("GL Entry", {"party_type": filters.party_type,
				"party": filters.party, "company": filters.company}, "account_currency")
			if gle_currency:
				account_currency = gle_currency
			else:
				account_currency = None if filters.party_type == "Employee" else \
					frappe.db.get_value(filters.party_type, filters.party, "default_currency")

		filters["account_currency"] = account_currency or filters.company_currency

		if filters.account_currency != filters.company_currency:
			filters["show_in_account_currency"] = 1

		return filters

def get_columns(filters):
	columns = [
		_("vi_Date") + ":Date:90", _("vi_Voucher") + ":Link/Journal Entry:300",
		_("vi_Debit") + ":Float:100", _("vi_Credit") + ":Float:100"
	]

	if filters.get("show_in_account_currency"):
		columns += [
			_("vi_Debit") + " (" + filters.account_currency + ")" + ":Float:100",
			_("vi_Credit") + " (" + filters.account_currency + ")" + ":Float:100"
		]

	columns += [
		_("vi_Remarks") + "::550"
	]

	return columns

def get_result(filters, account_details):
	gl_entries = get_gl_entries(filters)

	data = get_data_with_opening_closing(filters, account_details, gl_entries)

	result = get_result_as_list(data, filters)

	return result

def get_gl_entries(filters):
	select_fields = """, sum(debit_in_account_currency) as debit_in_account_currency,
		sum(credit_in_account_currency) as credit_in_account_currency""" \
		if filters.get("show_in_account_currency") else ""

	group_by_condition = "group by voucher_type, voucher_no, account, cost_center" \
		if filters.get("group_by_voucher") else "group by name"

	gl_entries = frappe.db.sql("""
		SELECT
			posting_date, account, party_type, party, name,	
			sum(debit) as debit, sum(credit) as credit,
			voucher_type, voucher_no, cost_center, project,
			against_voucher_type, against_voucher,
			REPLACE(remarks,'Reference #',' ') as remarks, against, is_opening {select_fields}
		from `tabGL Entry`
		where company=%(company)s {conditions}
		{group_by_condition}
		order by posting_date, account"""\
		.format(select_fields=select_fields, conditions=get_conditions(filters),
			group_by_condition=group_by_condition), filters, as_dict=1)

	return gl_entries

def get_conditions(filters):
	conditions = []
	if filters.get("account"):
		lft, rgt = frappe.db.get_value("Account", filters["account"], ["lft", "rgt"])
		conditions.append("""account in (select name from tabAccount
			where lft>=%s and rgt<=%s and docstatus<2)""" % (lft, rgt))

	if filters.get("voucher_no"):
		conditions.append("voucher_no=%(voucher_no)s")

	if filters.get("party_type"):
		conditions.append("party_type=%(party_type)s")

		if filters.get("party"):
			conditions.append("party=%(party)s")

	if not (filters.get("account") or filters.get("party") or filters.get("group_by_account")):
		conditions.append("posting_date >=%(from_date)s")

	if filters.get("project"):
		conditions.append("project=%(project)s")

	from frappe.desk.reportview import build_match_conditions
	match_conditions = build_match_conditions("GL Entry")
	if match_conditions: conditions.append(match_conditions)

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def get_data_with_opening_closing(filters, account_details, gl_entries):
	data = []
	gle_map = initialize_gle_map(gl_entries)

	totals, entries = get_accountwise_gle(filters, gl_entries, gle_map)

	# Opening for filtered account
	data.append(totals.opening)

	if filters.get("group_by_account"):
		for acc, acc_dict in gle_map.items():
			if acc_dict.entries:
				# opening
				data.append({})
				data.append(acc_dict.totals.opening)

				data += acc_dict.entries

				# totals
				data.append(acc_dict.totals.total)

				# closing
				data.append(acc_dict.totals.closing)
		data.append({})

	else:
		data += entries

	# totals
	data.append(totals.total)

	# closing
	data.append(totals.closing)

	#total closing
	total_closing = totals.total_closing
	total_debit = totals.closing.get('debit', 0)
	total_credit = totals.closing.get('credit', 0)
	debit_in_account_currency = totals.closing.get('debit_in_account_currency', 0)
	credit_in_account_currency = totals.closing.get('credit_in_account_currency', 0)

	total_amount = total_debit - total_credit

	if total_amount > 0:
		total_closing['debit'] = total_amount
		total_closing['debit_in_account_currency'] = debit_in_account_currency - credit_in_account_currency
	else:
		total_closing['credit'] = abs(total_amount)
		total_closing['credit_in_account_currency'] = abs(debit_in_account_currency - credit_in_account_currency)

	data.append(totals.total_closing)

	return data

def get_totals_dict():
	def _get_debit_credit_dict(label):
		return _dict(
			voucher_no = "'{0}'".format(label),
			debit = 0.0,
			credit = 0.0,
			debit_in_account_currency = 0.0,
			credit_in_account_currency = 0.0
		)
	return _dict(
		opening = _get_debit_credit_dict(_('vi_opening')),
		total = _get_debit_credit_dict(_('vi_total')),
		closing = _get_debit_credit_dict(_('vi_closing')),
		total_closing = _get_debit_credit_dict(_('vi_closing_balance'))
	)

def initialize_gle_map(gl_entries):
	gle_map = frappe._dict()
	for gle in gl_entries:
		gle_map.setdefault(gle.account, _dict(totals = get_totals_dict(), entries = []))
	return gle_map

def get_accountwise_gle(filters, gl_entries, gle_map):
	totals = get_totals_dict()
	entries = []

	def update_value_in_dict(data, key, gle):
		data[key].debit += flt(gle.debit)
		data[key].credit += flt(gle.credit)

		data[key].debit_in_account_currency += flt(gle.debit_in_account_currency)
		data[key].credit_in_account_currency += flt(gle.credit_in_account_currency)


	from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
	for gle in gl_entries:
		if gle.posting_date < from_date or cstr(gle.is_opening) == "Yes":
			update_value_in_dict(gle_map[gle.account].totals, 'opening', gle)
			update_value_in_dict(totals, 'opening', gle)
			
			update_value_in_dict(gle_map[gle.account].totals, 'closing', gle)
			update_value_in_dict(totals, 'closing', gle)

		elif gle.posting_date <= to_date:
			update_value_in_dict(gle_map[gle.account].totals, 'total', gle)
			update_value_in_dict(totals, 'total', gle)
			if filters.get("group_by_account"):
				gle_map[gle.account].entries.append(gle)
			else:
				entries.append(gle)

			update_value_in_dict(gle_map[gle.account].totals, 'closing', gle)
			update_value_in_dict(totals, 'closing', gle)

	return totals, entries

def get_result_as_list(data, filters):
	result = []
	for d in data:
		row = [d.get("posting_date"),d.get("voucher_no"), d.get("debit"), d.get("credit")]

		if filters.get("show_in_account_currency"):
			row += [d.get("debit_in_account_currency"), d.get("credit_in_account_currency")]

		row += [d.get("remarks")
		]

		result.append(row)

	return result