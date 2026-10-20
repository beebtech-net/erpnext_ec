import frappe
import os
import json
from types import SimpleNamespace
from lxml import etree
from xml.etree.ElementTree import Element, SubElement, tostring
from datetime import datetime
from dateutil import parser
from decimal import Decimal

from erpnext_ec.utils.secure_reader import (
    read_file_in_site,
    write_file_in_site,
    remove_file_in_site,
)


# Metodo que gestiona el upload de los archivos seleccionados
@frappe.whitelist()
def custom_upload(file=None):
    frappe.logger().info(file)

    file_content = frappe.local.uploaded_file
    file_name = frappe.local.uploaded_filename
    relative_path = "/private/files/" + file_name

    # your magic here to rename, check if file exists, change path ...

    write_file_in_site(relative_path, file_content, mode="wb")


def evaluate_supplier(create_if_not_exists, tax_id, supplier_name, nombreComercial, dirMatriz):
    found_data = frappe.get_all('Supplier', filters={"tax_id": tax_id, "name": supplier_name}, fields=['*'])

    if found_data:
        frappe.logger().info('Proveedor ya existe')
    else:
        frappe.logger().info('Proveedor NO existe')
        new_data = frappe.get_doc({
            "doctype": "Supplier",
            "tax_id": tax_id,
            "name": supplier_name,
            "nombreComercial": nombreComercial,
            "primary_address": dirMatriz,
            "is_internal_supplier": 0,
            "is_transporter": 0,
            "supplier_group": "Servicios"
        })

        new_data.insert()

def evaluate_item(create_if_not_exists, item_code, item_name, item_group, item_brand, item_description, item_standard_rate):
    frappe.logger().info('Buscar productos')
    frappe.logger().info("%s %s" % (item_code, item_name))
    # TODO: Revisar el filtro, no funciona si se combina item_code y item_name
    found_data = frappe.get_all('Item', fields='*', filters={"item_code": item_code})

    if found_data:
        frappe.logger().info('Item ya existe')
    else:
        frappe.logger().info('Item NO existe')
        new_data = frappe.get_doc({
            "doctype": "Item",
            "item_code": item_code,
            "item_name": item_name,
            "item_group": item_group,
            "brand": item_brand,
            "description": item_description,
            "standard_rate": item_standard_rate,
        })

        new_data.insert()


def evaluate_brand(create_if_not_exists, name_for_search):
    found_data = frappe.get_all('Brand', filters={"name": name_for_search})

    if found_data:
        frappe.logger().info('Marca ya existe')
    else:
        frappe.logger().info('Marca NO existe')
        new_data = frappe.get_doc({
            "doctype": "Brand",
            "name": name_for_search,
            "brand": name_for_search,
            "description": name_for_search
        })

        new_data.insert()

def evaluate_product_group(create_if_not_exists, name_for_search):
    found_data = frappe.get_all('Item Group', filters={"name": name_for_search})

    if found_data:
        frappe.logger().info('Grupo de producto ya existe')
    else:
        # Realizar la busqueda automatica de este nombre
        parent_item_group = "Todos los grupos de artículos"

        frappe.logger().info('Grupo de producto NO existe')
        new_data = frappe.get_doc({
            "doctype": "Item Group",
            "item_group_name": name_for_search,
            "parent_item_group": parent_item_group,
            "route": name_for_search
        })

        new_data.insert()

def search_account_tax(create_if_not_exists, codigo, codigoPorcentaje, tarifa):
    found_data_taxes_template = frappe.get_all('Purchase Taxes and Charges Template', fields=['*'])

    if found_data_taxes_template:
        for item_template in found_data_taxes_template:
            found_data_item_taxes_template = frappe.get_all(
                'Purchase Taxes and Charges',
                fields=['*'],
                filters={"parent": item_template.name}
            )

            for tax_detail in found_data_item_taxes_template:
                if (tax_detail.category == 'Total'
                        and tax_detail.add_deduct_tax == 'Add'
                        and tax_detail.charge_type == 'On Net Total'):
                    found_account = frappe.get_all(
                        'Account',
                        fields=['*'],
                        filters={"name": tax_detail.account_head}
                    )

                    for account_item in found_account:
                        frappe.logger().info("name: %s" % account_item.name)
                        frappe.logger().info("sricode: %s" % account_item.sricode)
                        frappe.logger().info("codigoporcentaje: %s" % account_item.codigoporcentaje)
                        frappe.logger().info("tax_rate: %s" % account_item.tax_rate)
                        frappe.logger().info("------------------------")
                        frappe.logger().info("%s %s %s" % (codigo, codigoPorcentaje, tarifa))

                        if (account_item.sricode == codigo
                                and account_item.codigoporcentaje == codigoPorcentaje
                                and account_item.tax_rate == float(tarifa)):
                            frappe.logger().info("Se encontro la cuenta que coincide...")
                            frappe.logger().info("Plantilla de impuesto de compra: %s" % item_template.name)
                            return account_item


def evaluate_taxes(create_if_not_exists, codigo, codigoPorcentaje, tarifa):
    found_data_taxes_template = frappe.get_all('Purchase Taxes and Charges Template', fields=['*'])

    if found_data_taxes_template:
        for item_template in found_data_taxes_template:
            found_data_item_taxes_template = frappe.get_all(
                'Purchase Taxes and Charges',
                fields=['*'],
                filters={"parent": item_template.name}
            )

            for tax_detail in found_data_item_taxes_template:
                if (tax_detail.category == 'Total'
                        and tax_detail.add_deduct_tax == 'Add'
                        and tax_detail.charge_type == 'On Net Total'):
                    found_account = frappe.get_all(
                        'Account',
                        fields=['*'],
                        filters={"name": tax_detail.account_head}
                    )

                    for account_item in found_account:
                        frappe.logger().info("name: %s" % account_item.name)
                        frappe.logger().info("sricode: %s" % account_item.sricode)
                        frappe.logger().info("codigoporcentaje: %s" % account_item.codigoporcentaje)
                        frappe.logger().info("tax_rate: %s" % account_item.tax_rate)
                        frappe.logger().info("------------------------")
                        frappe.logger().info("%s %s %s" % (codigo, codigoPorcentaje, tarifa))

                        if (account_item.sricode == codigo
                                and account_item.codigoporcentaje == codigoPorcentaje
                                and account_item.tax_rate == float(tarifa)):
                            frappe.logger().info("Se encontro la cuenta que coincide...")
                            frappe.logger().info("Plantilla de impuesto de compra: %s" % item_template.name)
                            return item_template


@frappe.whitelist()
def import_purchase_invoice_from_xml(file, auto_create_data, update_invoices, remove_files):
    frappe.logger().info(file)
    frappe.logger().info(auto_create_data)
    frappe.logger().info(update_invoices)
    frappe.logger().info(remove_files)

    file_json = json.loads(file, object_hook=lambda d: SimpleNamespace(**d))

    access_folder = '/public'
    if file_json.is_private:
        # access_folder = 'private' #NOT add is automatic on frappe.local.site
        # TODO: Check on 13 version
        access_folder = ''

    # file_url viene del cliente: se usa tal cual dentro del helper,
    # que valida que la ruta final no salga de sites/<site>/
    relative_path = access_folder + file_json.file_url

    xml_string_data = read_file_in_site(relative_path, mode="rb")

    doc_root = etree.fromstring(xml_string_data)

    # Se lee la cabecera del XML Autorizado
    for child in doc_root:
        if child.tag == "comprobante":
            doc_comprobante = etree.fromstring(child.text.encode('utf-8'))

            defaulProductGroup = 'Adquisiciones (DI)'
            defaultBrand = 'Sin Marca (DI)'

            found_purchase_invoice = frappe.get_all(
                'Purchase Invoice',
                filters={"numeroautorizacion": doc_comprobante.find('infoTributaria').find('claveAcceso').text},
                fields=['*']
            )

            if found_purchase_invoice:
                frappe.logger().info('Registro existente, no se creará nuevo')
                reference_purchase_invoice = found_purchase_invoice[0]
                return

            # Se analizan los datos para crear los requeridos en caso de que no existan

            # Evaluar grupo de productos
            evaluate_product_group(True, defaulProductGroup)

            # Evaluar marca de productos
            evaluate_brand(True, defaultBrand)

            # Evaluar Proveedor
            evaluate_supplier(
                True,
                doc_comprobante.find('infoTributaria').find('ruc').text,
                doc_comprobante.find('infoTributaria').find('razonSocial').text,
                doc_comprobante.find('infoTributaria').find('nombreComercial').text,
                doc_comprobante.find('infoTributaria').find('dirMatriz').text
            )

            frappe.logger().info('Registro nuevo')

            fechaAutorizacion = parser.parse(doc_root.find('fechaAutorizacion').text)

            new_tax_items = []

            for totalConImpuestoItem in doc_comprobante.find('infoFactura').find('totalConImpuestos'):
                found_account = search_account_tax(
                    True,
                    totalConImpuestoItem.find('codigo').text,
                    totalConImpuestoItem.find('codigoPorcentaje').text,
                    totalConImpuestoItem.find('tarifa').text
                )

                if found_account:
                    new_tax_item = {
                        "category": "Total",
                        "add_deduct_tax": "Add",
                        "charge_type": "On Net Total",
                        "account_head": found_account.name,
                        "description": found_account.account_name + "@" + str(found_account.tax_rate),
                        "rate": float(totalConImpuestoItem.find('tarifa').text),
                        "tax_amount": float(totalConImpuestoItem.find('valor').text),
                        "tax_amount_after_discount_amount": float(totalConImpuestoItem.find('valor').text),
                        "total": float(totalConImpuestoItem.find('baseImponible').text) + float(totalConImpuestoItem.find('valor').text),
                        "base_tax_amount": float(totalConImpuestoItem.find('valor').text)
                    }

                    new_tax_items.append(new_tax_item)

            for pagoItem in doc_comprobante.find('infoFactura').find('pagos'):
                frappe.logger().info("%s %s" % (pagoItem.tag, pagoItem.attrib))

            new_items = []
            idx_item = 0
            for detalleItem in doc_comprobante.find('detalles'):
                evaluate_item(
                    True,
                    detalleItem.find('codigoPrincipal').text,
                    detalleItem.find('descripcion').text,
                    defaulProductGroup,
                    defaultBrand,
                    detalleItem.find('descripcion').text,
                    float(detalleItem.find('precioUnitario').text)
                )

                new_item = {
                    "idx": idx_item,
                    "qty": float(detalleItem.find('cantidad').text),
                    "rate": float(detalleItem.find('precioUnitario').text),
                    "name": detalleItem.find('descripcion').text,
                    "item_name": detalleItem.find('descripcion').text,
                    "description": detalleItem.find('descripcion').text,
                    "item_code": detalleItem.find('codigoPrincipal').text,
                    "item_group": defaulProductGroup,
                    "parent": "",
                    "docstatus": "",
                    "amount": float(detalleItem.find('precioTotalSinImpuesto').text),
                    "brand": defaultBrand,
                    "parentfield": "",
                    "parenttype": "",
                    "product_bundle": ""
                }

                ++idx_item
                new_items.append(new_item)

                for detalleImpuestoItem in detalleItem.find('impuestos'):
                    purchase_taxes_and_charges_template = evaluate_taxes(
                        True,
                        detalleImpuestoItem.find('codigo').text,
                        detalleImpuestoItem.find('codigoPorcentaje').text,
                        detalleImpuestoItem.find('tarifa').text
                    )

                    if not purchase_taxes_and_charges_template:
                        frappe.logger().info("DEBE SALIR AQUI")
                        frappe.logger().info(
                            "Los impuestos deben estar configurados en el sistema. "
                            "Plantilla de impuesto de compras, códigos del SRI."
                        )

            infoAdicional = []
            for infoAdicionalItem in doc_comprobante.find('infoAdicional'):
                if infoAdicionalItem.tag == 'campoAdicional':
                    infoAdicional.append({
                        "nombre": infoAdicionalItem.attrib['nombre'],
                        "valor": infoAdicionalItem.text
                    })

            n_secuencial = int(doc_comprobante.find('infoTributaria').find('secuencial').text)

            docidsri = (
                doc_comprobante.find('infoTributaria').find('estab').text
                + '-'
                + doc_comprobante.find('infoTributaria').find('ptoEmi').text
                + '-'
                + f'{n_secuencial:09d}'
            )

            bill_date = parser.parse(doc_comprobante.find('infoFactura').find('fechaEmision').text)

            new_purchase_invoice_ = {
                "docstatus": 0,
                "doctype": "Purchase Invoice",
                "numeroautorizacion": doc_comprobante.find('infoTributaria').find('claveAcceso').text,
                "supplier": doc_comprobante.find('infoTributaria').find('razonSocial').text,
                "secuencial": doc_comprobante.find('infoTributaria').find('secuencial').text,
                "sri_ambiente": int(doc_comprobante.find('infoTributaria').find('ambiente').text),
                "sri_estado": 200,
                "sri_response": 'AUTORIZADO',
                "docidsri": docidsri,
                "fechaautorizacion": fechaAutorizacion.replace(tzinfo=None),
                "bill_no": docidsri,
                "bill_date": bill_date.replace(tzinfo=None),
                "is_sri_imported": True,
                "items": new_items,
                "taxes": new_tax_items,
                "infoadicional": infoAdicional
            }

            # Se crea nueva factura de compra importada
            reference_purchase_invoice = frappe.get_doc(new_purchase_invoice_)
            reference_purchase_invoice.insert()
            reference_purchase_invoice.save()

    if remove_files:
        frappe.logger().info(relative_path)
        try:
            remove_file_in_site(relative_path)
        except FileNotFoundError:
            pass