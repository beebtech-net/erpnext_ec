import os
import frappe

def read_file_in_app(app_name, *path_parts):
    app_root = os.path.realpath(frappe.get_app_path(app_name))
    requested = os.path.realpath(frappe.get_app_path(app_name, *path_parts))
    if not requested.startswith(app_root + os.sep):
        frappe.throw(f"Ruta no permitida: {path_parts}")
    with open(requested) as f:
        return f.read()