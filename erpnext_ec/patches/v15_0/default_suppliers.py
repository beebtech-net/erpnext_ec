from __future__ import unicode_literals
from frappe import __version__ as frappe_version
import frappe
import json
import os

COMPANY_SUPPLIER_FIELD = "sri_electronic_documents_supplier"
DEFAULT_SUPPLIER_GROUP = "All Supplier Groups"  # ajusta si tu sitio usa otro nombre


def execute():
    supplier_list = [
        {
            "supplier_name": "Raul Borbor",
            "supplier_group": ["Servicios", "Services"],
            "supplier_type": "Company",
            "tax_id": "0915885404001",
            "es_proveedor_servicios_documentos_electronicos_sri": 1,
        },

        # Futuros proveedores predeterminados:
        # {
        #     "supplier_name": "Otro Proveedor",
        #     "supplier_group": "Servicios",
        #     "supplier_type": "Company",
        #     "tax_id": "RUC_DEL_PROVEEDOR",
        #     "es_proveedor_servicios_documentos_electronicos_sri": 1,
        # },
    ]

    print("Configurando proveedores predeterminados")

    for supplier_item in supplier_list:
        supplier_name = create_supplier(supplier_item)

        # Asignar únicamente los proveedores marcados
        # expresamente para este propósito.
        if supplier_item.get("assign_to_companies", 0):
            assign_supplier_to_companies(supplier_name)


def create_supplier(supplier_data):
    supplier_name = supplier_data["supplier_name"]
    tax_id = supplier_data.get("tax_id")

    # Comprobar si existe por nombre.
    existing_by_name = frappe.db.get_value(
        "Supplier",
        {"supplier_name": supplier_name},
        "name",
    )

    # Comprobar si existe por RUC.
    existing_by_tax_id = None

    if tax_id:
        existing_by_tax_id = frappe.db.get_value(
            "Supplier",
            {"tax_id": tax_id},
            "name",
        )

    # Si el nombre y el RUC corresponden a proveedores
    # diferentes, detener el proceso para evitar errores.
    if (
        existing_by_name
        and existing_by_tax_id
        and existing_by_name != existing_by_tax_id
    ):
        frappe.throw(
            "El nombre y el RUC de "
            + supplier_name
            + " corresponden a proveedores diferentes."
        )

    # Si ya existe por nombre o RUC, reutilizarlo.
    existing_supplier = existing_by_name or existing_by_tax_id

    if existing_supplier:
        print(
            "El proveedor ya existe: "
            + existing_supplier
        )
        return existing_supplier

    # Validar que exista el grupo de proveedores.
    raw = supplier_data["supplier_group"]
    candidatos = raw if isinstance(raw, (list, tuple)) else [raw]
    candidatos = [str(c).strip() for c in candidatos if c]

    supplier_group = None
    for g in candidatos:
        supplier_group = frappe.db.get_value(
            "Supplier Group", {"name": g}, "name"
        ) or frappe.db.get_value(
            "Supplier Group", {"supplier_group_name": g}, "name"
        )
        if supplier_group:
            break

    if not supplier_group:
        frappe.log_error(
            message="Candidatos: " + ", ".join(candidatos),
            title="Grupo de proveedores no encontrado: " + supplier_name,
        )
        supplier_group = frappe.db.get_value(
            "Supplier Group", {"is_group": 1, "parent_supplier_group": ""}, "name"
        ) or frappe.db.get_value("Supplier Group", {"is_group": 1}, "name")

    if not supplier_group:
        frappe.throw(
            "No hay ningún Supplier Group válido en el sitio. "
            "Crea al menos uno antes de ejecutar esto."
        )

    supplier_doc = frappe.get_doc({
        "doctype": "Supplier",
        "supplier_name": supplier_name,
        "supplier_group": supplier_group,
        "supplier_type": supplier_data["supplier_type"],
        "tax_id": tax_id,
        "es_proveedor_servicios_documentos_electronicos_sri":
            supplier_data.get(
                "es_proveedor_servicios_documentos_electronicos_sri",
                0,
            ),
    })

    supplier_doc.insert(ignore_permissions=True)

    print("Instalado Supplier: " + supplier_doc.name)

    return supplier_doc.name


def assign_supplier_to_companies(supplier_name):
    # Verificar que el campo personalizado exista.
    company_meta = frappe.get_meta("Company")

    if not company_meta.has_field(COMPANY_SUPPLIER_FIELD):
        frappe.throw(
            "No existe el campo personalizado "
            + COMPANY_SUPPLIER_FIELD
            + " en Company. Verifica que se cree antes "
            "de ejecutar la configuración de proveedores."
        )

    companies = frappe.get_all(
        "Company",
        fields=["name", COMPANY_SUPPLIER_FIELD],
    )

    assigned_count = 0

    for company in companies:
        # No sobrescribir un proveedor ya seleccionado.
        if not company.get(COMPANY_SUPPLIER_FIELD):
            frappe.db.set_value(
                "Company",
                company.name,
                COMPANY_SUPPLIER_FIELD,
                supplier_name,
            )

            assigned_count += 1

            print(
                "Proveedor "
                + supplier_name
                + " asignado a Company "
                + company.name
            )

    print(
        "Compañías actualizadas: "
        + str(assigned_count)
    )