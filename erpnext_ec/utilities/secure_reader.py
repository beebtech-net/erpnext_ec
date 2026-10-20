import os
import frappe


def _validate_inside(base_path, requested_path, label=""):
    """Valida que requested_path esté dentro de base_path."""
    base_path = os.path.realpath(base_path)
    requested_path = os.path.realpath(requested_path)
    if not requested_path.startswith(base_path + os.sep) and requested_path != base_path:
        frappe.throw(f"Ruta no permitida {label}: {requested_path}")
    return requested_path


def read_file_in_app(app_name, *path_parts):
    app_root = os.path.realpath(frappe.get_app_path(app_name))
    requested = os.path.realpath(frappe.get_app_path(app_name, *path_parts))
    if not requested.startswith(app_root + os.sep):
        frappe.throw(f"Ruta no permitida: {path_parts}")
    with open(requested, "rb") as f:
        return f.read()


def read_file_in_site(relative_path, mode="rb"):
    """Lee un archivo dentro de sites/<site>/ validando traversal."""
    site_root = frappe.get_site_path()
    requested = _validate_inside(site_root, site_root + relative_path, label="(site)")
    with open(requested, mode) as f:
        return f.read()


def write_file_in_site(relative_path, content, mode="w"):
    """Escribe un archivo dentro de sites/<site>/ validando traversal."""
    site_root = frappe.get_site_path()
    requested = _validate_inside(site_root, site_root + relative_path, label="(site)")
    with open(requested, mode) as f:
        f.write(content)
    return requested


def remove_file_in_site(relative_path):
    """Elimina un archivo dentro de sites/<site>/ validando traversal."""
    site_root = frappe.get_site_path()
    requested = _validate_inside(site_root, site_root + relative_path, label="(site)")
    if os.path.exists(requested):
        os.remove(requested)