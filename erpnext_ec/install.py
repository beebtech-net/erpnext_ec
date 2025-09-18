from __future__ import unicode_literals
from frappe import __version__ as frappe_version
import frappe
import json
import os
#from frappe.utils import validate_email_address, split_emails
from erpnext_ec.patches.v15_0.custom_fields import *

import click
# from ec_extend.setup import after_install as setup

def before_install():
	print('before_install')
	#print('Eliminando columnas de datos del modo antiguo')
	#remove_old_columns()

def after_install():
	try:
		print("Setting ERPNext Ecuador...")
		# setup()

		click.secho("Thank you for installing ERPNext Ecuador!", fg="green")

	except Exception as e:
		#BUG_REPORT_URL = "https://github.com/frappe/hrms/issues/new"
		#click.secho(
	#		"Installation for ERPNext Ecuador app failed due to an error."
	#		" Please try re-installing the app or"
#			f" report the issue on {BUG_REPORT_URL} if not resolved.",
#			fg="bright_red",
		#)

		click.secho(
			"Installation for ERPNext Ecuador app failed due to an error."
			" Please try re-installing the app.",
			fg="bright_red",
		)

		raise e	
	