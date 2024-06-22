# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals

import frappe
from frappe.model.document import Document
from erpnext.accounts.doctype.journal_entry.journal_entry import get_payment_entry
from erpnext.accounts.doctype.journal_entry.journal_entry import JournalEntry

class PurchaseWithholdingSriEc(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	pass
	
	def set_status(self, update=False, status=None, update_modified=True):
		#if self.is_new():
		#	if self.get("amended_from"):
		#		self.status = "Draft"
		#	return

		self.status = "Submitted"

		if update:
			self.db_set("status", self.status, update_modified=update_modified)

	def on_submit(self):
		print('submit!!')
		print('Proceso de asientos contables')
		self.create_journal_entry()
	
	def set_purchase_withholding_supplier(self):
		print('set_purchase_withholding_supplier')
		pass

	def validate(self):
		print('validate_link')
		self.set_status()
		
		pass
	
	def create_journal_entry(self):
        # Define the necessary data for the journal entry
		journal_entry = frappe.new_doc('Journal Entry')
		journal_entry.voucher_type = 'Journal Entry'
		journal_entry.company = self.company
		journal_entry.pay_to_recd_from = self.purchase_withholding_supplier
		journal_entry.posting_date = frappe.utils.nowdate()
		journal_entry.user_remark = f'Journal Entry for Purchase Withholding {self.name}'
		journal_entry.remark = f'Journal Entry for Purchase Withholding {self.name}'
		journal_entry.title = f'AUTO-{self.name}'
		journal_entry.write_off_based_on = "Accounts Receivable"

		#journal_entry.bill_no = "Accounts Receivable"
		#journal_entry.bill_date = "Accounts Receivable"
		#journal_entry.due_date = "Accounts Receivable"

		account_for_withHolding = '2110 - Acreedores - RSCV'

		total_credit_in_account_currency = 0
		#Linea de cuenta de Acreedores
		for itemTax in self.taxes:			
			# Add entries to the journal entry
			total_credit_in_account_currency += itemTax.valorRetenido
			
		journal_entry.append('accounts', {
            'account': account_for_withHolding,
			'account_type':'Payable',
			"against_account": self.purchase_withholding_supplier,
			"doctype": "Journal Entry Account",
			'debit': 0,
            'debit_in_account_currency': 0,
			'credit': total_credit_in_account_currency,
            'credit_in_account_currency': total_credit_in_account_currency,
            'party_type': 'Supplier',
            'party': self.purchase_withholding_supplier  # Replace with the actual supplier field
        })

		for itemTax in self.taxes:			
			# Add entries to the journal entry
			journal_entry.append(
				'accounts', {
					'account': itemTax.codigoRetencion,
					'debit': itemTax.valorRetenido,
            		'debit_in_account_currency': itemTax.valorRetenido,
					'credit': 0,
					'credit_in_account_currency': 0,
					'party_type': 'Supplier',
					'party': self.purchase_withholding_supplier
				})


        # Save and submit the journal entry
		journal_entry.save(ignore_permissions=True)
		journal_entry.submit()

	def before_save(self):
		print('before_save')
        # Acceder a los datos del detalle y realizar acciones en función de los cambios
        #for row in self.table_fieldname:
            # Realizar acciones necesarias en función de los valores de los campos en el detalle
        #    if row.my_fieldname:
                # Realizar alguna acción si el campo my_fieldname tiene un valor específico
        #        pass

# <infoTributaria>
# 		<ambiente>2</ambiente>
# 	    <tipoEmision>1</tipoEmision>
# 	    <razonSocial>COBOS MERO VICTOR HUGO</razonSocial>
# 	    <nombreComercial>COBOS MERO VICTOR HUGO</nombreComercial>
# 	    <ruc>1205019688001</ruc>
# 	    <claveAcceso>1105202107120501968800120010010000000252443850112</claveAcceso>
# 	    <codDoc>07</codDoc>
# 	    <estab>001</estab>
# 	    <ptoEmi>001</ptoEmi>
# 	    <secuencial>000000025</secuencial>
# 	    <dirMatriz>GUAYAS / GUAYAQUIL / TARQUI / SOLAR 33	</dirMatriz>		
# 		<agenteRetencion>1</agenteRetencion>		
#  </infoTributaria>
#  <infoCompRetencion>
# 	    <fechaEmision>11/05/2021</fechaEmision>
# 	    <obligadoContabilidad>SI</obligadoContabilidad>
# 	    <tipoIdentificacionSujetoRetenido>04</tipoIdentificacionSujetoRetenido>
# 	    <razonSocialSujetoRetenido>Raul Vinicio Borbor Torres</razonSocialSujetoRetenido>
# 	    <identificacionSujetoRetenido>0915885404001</identificacionSujetoRetenido>
# 	    <periodoFiscal>05/2021</periodoFiscal>
#  </infoCompRetencion>