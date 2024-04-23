import frappe
import os
import json
from types import SimpleNamespace
from lxml import etree
from xml.etree.ElementTree import Element, SubElement, tostring
from datetime import datetime

@frappe.whitelist()
def custom_upload(file = None):
    print(file)

    file_content = frappe.local.uploaded_file
    file_name = frappe.local.uploaded_filename
    file_path = frappe.local.site + "/private/files/" + file_name
    
    #print(file_content)
    #print(file_name)
    #print(file_path)
    # your magic here to rename, check if file exists, change path ...

    with open(file_path, "wb") as file:
        file.write(file_content)

def evaluate_supplier(create_if_not_exists, tax_id, supplier_name, nombreComercial, dirMatriz):
    found_data = frappe.get_all('Supplier', filters={"tax_id": tax_id, "name": supplier_name}, fields = ['*'])

    if (found_data):
        pass
    else:
        new_data = frappe.get_doc({
            "doctype": "Supplier",
            "tax_id":  tax_id,
            "name":  supplier_name,
            "nombreComercial":  nombreComercial,
            "primary_address":  dirMatriz,
            "is_internal_supplier":  0,
            "is_transporter":  0,
            "supplier_group":  "Servicios"
        })

        new_data.insert()

def evaluate_item(create_if_not_exists, item_code, item_name, item_group, item_brand, item_description, item_standard_rate):
    found_data = frappe.get_all('Item', filters={"code": item_code, "name": item_name}, fields = ['*'])

    if (found_data):
        pass
    else:
        new_data = frappe.get_doc({
            "doctype": "Item",
            "code":  item_code,
            "name":  item_name,
            "group":  item_group,
            "brand":  item_brand,
            "description":  item_description,
            "standard_rate":  item_standard_rate,
        })

        new_data.insert()

def evaluate_brand(create_if_not_exists, name_for_search):
    found_data = frappe.get_all('Brand', filters={"name": name_for_search})

    if (found_data):
        pass
    else:
        new_data = frappe.get_doc({
            "doctype": "Brand",
            "name":  name_for_search,
            "brand":  name_for_search,
            "description":  name_for_search
        })

        new_data.insert()

def evaluate_product_group(create_if_not_exists, name_for_search):
    found_data = frappe.get_all('Item Group', filters={"name": name_for_search})

    if (found_data):
        pass
    else:
        new_data = frappe.get_doc({
            "doctype": "Item Group",
            "name":  name_for_search,
            "parent_item_group":  name_for_search,
            "route":  name_for_search
        })

        new_data.insert()

def evaluate_taxes(create_if_not_exists, name_for_search):
    found_purchase_invoice = frappe.get_all('Sales Invoice', filters={"numeroautorizacion": doc_comprobante.find('infoTributaria').find('claveAcceso').text}, fields = ['*'])


@frappe.whitelist()
def import_purchase_invoice_from_xml(file, auto_create_data, update_invoices, remove_files):
    print(file)
    #print(file.is_private)
    print(auto_create_data)
    print(update_invoices)
    print(remove_files)

    file_json = json.loads(file, object_hook=lambda d: SimpleNamespace(**d))

    access_folder = '/public'
    if(file_json.is_private):
        #access_folder = 'private' #NOT add is automatic on frappe.local.site
        #TODO: Check on 13 version
        access_folder = ''

    #file_content = frappe.local.uploaded_file
    #file_name = frappe.local.uploaded_filename
    #file_path = frappe.local.site + "/private/files/" + file_name
    
    #print(file_content)
    #print(file_name)
    #print(file_path)
    # your magic here to rename, check if file exists, change path ...

    #with open(file_path, "wb") as file:
    #    file.write(file_content)

    file_path = frappe.local.site + access_folder + file_json.file_url

    f=open(file_path, "rb")
    xml_string_data=f.read()
    f.close()
    
    doc_root = etree.fromstring(xml_string_data)

    #print(doc_root)

    #Se lee la cabecera del XML Autorizado
    for child in doc_root:
        #print(child.tag, child.attrib)
        if(child.tag == "comprobante"):
            print("Leer contenido")
            #print(child.text)
            #doc_comprobante = etree.fromstring(b'' + child.text)
            doc_comprobante = etree.fromstring(child.text.encode('utf-8'))
            #print(doc_comprobante)

            #purchase_invoice_doc = frappe.get_last_doc("Purchase Invoice", doc_comprobante.find('infoTributaria').find('claveAcceso').text)
            found_purchase_invoice = frappe.get_all('Sales Invoice', filters={"numeroautorizacion": doc_comprobante.find('infoTributaria').find('claveAcceso').text}, fields = ['*'])

            new_purchase_invoice___ = {
                "docstatus": 0,
			    "doctype": "Purchase Invoice",
                "numeroautorizacion": doc_comprobante.find('infoTributaria').find('claveAcceso').text
            }

            if(not found_purchase_invoice):
                print('Registro nuevo')
                #new_client_script = frappe.get_doc(new_purchase_invoice)
                reference_purchase_invoice = frappe.get_doc(doctype='Purchase Invoice')
                reference_purchase_invoice.numeroautorizacion = doc_comprobante.find('infoTributaria').find('claveAcceso').text
                #Requeridos
                reference_purchase_invoice.supplier = 'RUEDA SANCHEZ JUAN CARLOS'
                reference_purchase_invoice.base_grand_total = 0
                reference_purchase_invoice.grand_total = 0

                reference_purchase_invoice.items

                reference_purchase_invoice.insert()
            else:
                print('Registro exitente')
                reference_purchase_invoice = found_purchase_invoice[0]

            reference_purchase_invoice.db_set('sri_estado', 200)

            print(doc_comprobante.find('infoTributaria').find('ambiente').text)
            print(doc_comprobante.find('infoTributaria').find('tipoEmision').text)
            print(doc_comprobante.find('infoTributaria').find('razonSocial').text)
            print(doc_comprobante.find('infoTributaria').find('nombreComercial').text)
            print(doc_comprobante.find('infoTributaria').find('ruc').text)
            print(doc_comprobante.find('infoTributaria').find('claveAcceso').text)
            print(doc_comprobante.find('infoTributaria').find('codDoc').text)
            print(doc_comprobante.find('infoTributaria').find('estab').text)
            print(doc_comprobante.find('infoTributaria').find('ptoEmi').text)
            print(doc_comprobante.find('infoTributaria').find('secuencial').text)
            print(doc_comprobante.find('infoTributaria').find('dirMatriz').text)

            print(doc_comprobante.find('infoFactura').find('fechaEmision').text)
            print(doc_comprobante.find('infoFactura').find('dirEstablecimiento').text)
            print(doc_comprobante.find('infoFactura').find('contribuyenteEspecial').text)
            print(doc_comprobante.find('infoFactura').find('obligadoContabilidad').text)
            print(doc_comprobante.find('infoFactura').find('tipoIdentificacionComprador').text)
            print(doc_comprobante.find('infoFactura').find('razonSocialComprador').text)
            print(doc_comprobante.find('infoFactura').find('identificacionComprador').text)
            print(doc_comprobante.find('infoFactura').find('totalSinImpuestos').text)
            print(doc_comprobante.find('infoFactura').find('totalDescuento').text)

            print(doc_comprobante.find('infoFactura').find('totalConImpuestos').text)

            for totalConImpuestoItem in doc_comprobante.find('infoFactura').find('totalConImpuestos'):
                print(totalConImpuestoItem.tag, totalConImpuestoItem.attrib)
                print(totalConImpuestoItem.find('codigo').text)
                print(totalConImpuestoItem.find('codigoPorcentaje').text)
                print(totalConImpuestoItem.find('baseImponible').text)
                print(totalConImpuestoItem.find('tarifa').text)
                print(totalConImpuestoItem.find('valor').text)            

            print(doc_comprobante.find('infoFactura').find('propina').text)
            print(doc_comprobante.find('infoFactura').find('importeTotal').text)
            print(doc_comprobante.find('infoFactura').find('moneda').text)

            for pagoItem in doc_comprobante.find('infoFactura').find('pagos'):
                print(pagoItem.tag, pagoItem.attrib)
                print(pagoItem.find('formaPago').text)
                print(pagoItem.find('total').text)
                print(pagoItem.find('plazo').text)
                print(pagoItem.find('unidadTiempo').text)
            
            for detalleItem in doc_comprobante.find('detalles'):
                print(detalleItem.tag, detalleItem.attrib)
                print(detalleItem.find('codigoPrincipal').text)
                print(detalleItem.find('descripcion').text)
                print(detalleItem.find('cantidad').text)
                print(detalleItem.find('precioUnitario').text)
                print(detalleItem.find('descuento').text)
                print(detalleItem.find('precioTotalSinImpuesto').text)
                for detalleImpuestoItem in detalleItem.find('impuestos'):
                    print(detalleImpuestoItem.tag, detalleImpuestoItem.attrib)
                    print(detalleImpuestoItem.find('codigo').text)
                    print(detalleImpuestoItem.find('codigoPorcentaje').text)
                    print(detalleImpuestoItem.find('tarifa').text)
                    print(detalleImpuestoItem.find('baseImponible').text)
                    print(detalleImpuestoItem.find('valor').text)

            for infoAdicionalItem in doc_comprobante.find('infoAdicional'):
                #print(infoAdicionalItem.tag, infoAdicionalItem.attrib)
                if(infoAdicionalItem.tag == 'campoAdicional'):
                    print(infoAdicionalItem.attrib['nombre'])
                    print(infoAdicionalItem.text)

            #for child_comprobante in doc_comprobante:
                #print(child_comprobante.tag, child_comprobante.attrib)
            #    if(child_comprobante.tag == "infoTributaria"):
            #        print(child_comprobante.find('claveAcceso').text)


    if(remove_files):
        
        print(file_path)
        if os.path.exists(file_path):
            os.remove(file_path)