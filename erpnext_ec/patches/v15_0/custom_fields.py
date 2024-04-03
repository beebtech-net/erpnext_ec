from __future__ import unicode_literals
import frappe
import os
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from frappe.model.meta import get_meta

def rename_old_columns():
    #And backup
    print('before_execute - Rename old Custom Fields')

    custom_fields_found = frappe.get_all("Custom Field", filters={"fieldname": "formapago", "dt": "Mode Of Payment"})
    if custom_fields_found:
        print('Campo encontrado')
        print(custom_fields_found)
        
        #rename_custom_field("Mode Of Payment", "formapago", "formapago_remove")
        meta = get_meta("Mode Of Payment")
        #meta.get_field("formapago").fieldname = "formapago_remove"

        print(meta.get_field("formapago"))
        print(meta.get_field("formapago").fieldname)
        print(meta.get_field("formapago").fieldtype)

        doctype = "Mode Of Payment"

        df = dict(
            fieldname="formapago_remove",
            label="formapago_remove",
            fieldtype="Data",
            insert_after="formaPago",
            options= '',
            hidden=0,
            print_hide=0,
            read_only=0,
        )
        
        # cf = create_custom_field("Mode Of Payment", df)

        is_system_generated = True
        ignore_validate = True
        custom_field = frappe.get_doc(
			{
				"doctype": "Custom Field",
				"dt": doctype,
				"permlevel": 0,
				"fieldtype": "Data",
				"hidden": 0,
				"is_system_generated": is_system_generated,
			}
		)
        
        custom_field.update(df)
        custom_field.flags.ignore_validate = ignore_validate
        #custom_field.delete(df)
        #frappe.delete_doc("Custom Field", "Mode of Payment-formapago_remove")
        #frappe.db.commit()
        #custom_field.insert(df)

        print (custom_field)

        #frappe.get_doc({
        #    "doctype": "Custom Field",
        #    "fieldname": "formapago_remove",
        #    "label": "formapago_remove",
        #    "insert_after": "formaPago",
        #    "dt": "Mode Of Payment",
        #    "fieldtype": "Data",
        #    "options": "",
        #    "permlevel": 0,
        #    "reqd": 0,
        #    "hide_in_list": 0,
        #    "in_filter": 0,
        #    "is_custom_field": 1,
        #    "translatable": 0,
        #    "default": "",
        #    "search_index": 0
        #}).insert()

        #meta.add_custom_fields({
        #    "fieldname": "formapago_remove",
        #    "label": "formapago_remove",
        #    "fieldtype": "Data"
        #})

        #meta.save()

def remove_old_columns():
    #And backup
    print('before_execute - Rename old Custom Fields')

    if frappe.get_all("Custom Field", filters={"fieldname": "formapago", "dt": "Mode Of Payment"}):
        print('Secuencial para el SRI')
        #delete_custom_fields("Mode Of Payment", "formapago", "formapago_remove")


def add_new_columns():
    # Actualizacion de datos en los campos custom de módulos
    # estos datos serán extraidos desde los campos custom anteriores (en caso de ser encontrados)
    # estos campos previamente han sido renombrados y serán eliminados al terminar la migración de datos
    print('after_install - Remove old Custom Fields')
    #delete_custom_fields("Mode Of Payment", ["formapago"])