from __future__ import unicode_literals
import frappe
import os

from frappe.model.meta import rename_custom_field
from frappe.model.meta import delete_custom_fields

#def execute():
def before_execute():
    print('before_execute - Rename old Custom Fields')

    if frappe.get_all("Custom Field", filters={"fieldname": "formapago", "dt": "Mode Of Payment"}):
        print('Secuencial para el SRI')        
        rename_custom_field("Mode Of Payment", "formapago", "formapago_remove")

def after_install():
    # Actualizacion de datos en los campos custom de módulos
    # estos datos serán extraidos desde los campos custom anteriores (en caso de ser encontrados)
    # estos campos previamente han sido renombrados y serán eliminados al terminar la migración de datos
    print('after_install - Remove old Custom Fields')
    delete_custom_fields("Mode Of Payment", ["formapago"])