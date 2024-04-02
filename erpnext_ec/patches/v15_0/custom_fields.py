from __future__ import unicode_literals
import frappe
import os

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
        meta.get_field("formapago").fieldname = "formapago_remove"
        meta.save()

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