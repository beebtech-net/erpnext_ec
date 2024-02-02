from __future__ import unicode_literals
import frappe
import os

#def after_install():
    # Llama a la función que agrega campos personalizados
#    agregar_campos_personalizados()

def execute():
    
    print('Sales Invoices Custom Fields')

    if not frappe.get_all("Custom Field", filters={"fieldname": "sri_sequence", "dt": "Sales Invoice"}):
        print('Secuencial para el SRI')

        frappe.get_doc({
            "doctype": "Custom Field",
            "fieldname": "sri_sequence",
            "label": "Secuencial para el SRI",
            "insert_after": "tax_id",
            "dt": "Sales Invoice",
            "fieldtype": "Int",
            "options": "",
            "permlevel": 0,
            "reqd": 0,
            "hide_in_list": 0,
            "in_filter": 0,
            "is_custom_field": 1,
            "translatable": 0,
            "default": "",
            "search_index": 0
        }).insert()