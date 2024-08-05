from frappe.model.document import Document
class SriEstablishmentLink(Document):
	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		description: DF.SmallText
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		row_id: DF.Data | None	
	pass


##
##from frappe import _

##def define_tables():
    ##return [
        ##{
            ##"doctype": "Mi Modelo",
            ##"fields": [
            ##    {"fieldname": "campo1", "label": _("Campo 1"), "fieldtype": "Data"},
            ##    {"fieldname": "campo2", "label": _("Campo 2"), "fieldtype": "Int"},
            ##    {"fieldname": "campo3", "label": _("Campo 3"), "fieldtype": "Date"},
            ##],
        ##}
    ##]