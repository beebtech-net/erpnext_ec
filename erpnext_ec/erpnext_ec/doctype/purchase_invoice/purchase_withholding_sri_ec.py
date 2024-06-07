# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals

import frappe
from frappe.model.document import Document

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
	
	def set_purchase_withholding_supplier(self):
		print('set_purchase_withholding_supplier')
		pass

	def validate(self):
		print('validate_link')
		self.set_status()
		pass

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