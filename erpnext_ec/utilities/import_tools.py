import frappe
import os
import json
from types import SimpleNamespace
from lxml import etree
from xml.etree.ElementTree import Element, SubElement, tostring
from datetime import datetime
from dateutil import parser
from decimal import Decimal

#Metodo que gestiona el upload de los archivos seleccionados
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
        print('Proveedor ya existe')
        pass
    else:
        print('Proveedor NO existe')
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
        frappe.db.commit()

def evaluate_item(create_if_not_exists, item_code, item_name, item_group, item_brand, item_description, item_standard_rate):
    print('Buscar productos')
    print(item_code, item_name)
    #TODO: Revisar el filtro, no funciona si se combina item_code y item_name
    #found_data = frappe.get_all('Item', filters={"item_code": item_code, "item_name": item_name})
    #found_data = frappe.get_all('Item', fields='*', filters=[["item_code", "=", item_code],["item_name", "=", item_name]])
    found_data = frappe.get_all('Item', fields='*', filters={"item_code":item_code})

    #print(found_data)

    if (found_data):
        print('Item ya existe')
        pass
    else:
        print('Item NO existe')
        new_data = frappe.get_doc({
            "doctype": "Item",
            "item_code":  item_code,
            "item_name":  item_name,
            "item_group":  item_group,
            "brand":  item_brand,
            "description":  item_description,
            "standard_rate":  item_standard_rate,
        })

        new_data.insert()
        frappe.db.commit()

def evaluate_brand(create_if_not_exists, name_for_search):
    found_data = frappe.get_all('Brand', filters={"name": name_for_search})

    if (found_data):
        print('Marca ya existe')
        pass
    else:
        print('Marca NO existe')
        new_data = frappe.get_doc({
            "doctype": "Brand",
            "name":  name_for_search,
            "brand":  name_for_search,
            "description":  name_for_search
        })

        new_data.insert()
        frappe.db.commit()

def evaluate_product_group(create_if_not_exists, name_for_search):
    found_data = frappe.get_all('Item Group', filters={"name": name_for_search})

    if (found_data):
        print('Grupo de producto ya existe')
        pass
    else:

        #Realizar la busqueda automatica de este nombre
        parent_item_group = "Todos los grupos de artículos"

        print('Grupo de producto NO existe')
        new_data = frappe.get_doc({
            "doctype": "Item Group",
            "item_group_name":  name_for_search,
            "parent_item_group":  parent_item_group,
            "route":  name_for_search
        })

        new_data.insert()
        frappe.db.commit()

def search_account_tax(create_if_not_exists, codigo, codigoPorcentaje, tarifa):
    found_data_taxes_template = frappe.get_all('Purchase Taxes and Charges Template', fields = ['*'])
    #print(found_data_taxes_template)

    if(found_data_taxes_template):
        for item_template in found_data_taxes_template:
            
            #print(item_template.name)
            found_data_item_taxes_template = frappe.get_all('Purchase Taxes and Charges', fields = ['*'], filters={"parent": item_template.name})
            #print("found_data_item_taxes_template")
            #print(found_data_item_taxes_template)

            #Buscar Items de la Plantilla
            for tax_detail in found_data_item_taxes_template:
                #print("Cuenta de impuestos:", tax_detail.account_head)
                #print("Tasa de impuestos:", tax_detail.rate)
                
                #print("add_deduct_tax:", tax_detail.add_deduct_tax)
                #print("category:", tax_detail.category)
                #print("charge_type:", tax_detail.charge_type)

                if(tax_detail.category == 'Total' and tax_detail.add_deduct_tax == 'Add' and tax_detail.charge_type == 'On Net Total'):
                    found_account = frappe.get_all('Account', fields = ['*'], filters={"name": tax_detail.account_head})

                    #print(found_account)

                    for account_item in found_account:
                        print("name:", account_item.name)
                        print("sricode:", account_item.sricode)
                        print("codigoporcentaje:", account_item.codigoporcentaje)
                        print("tax_rate:", account_item.tax_rate)
                        print("------------------------")
                        print(codigo, codigoPorcentaje, tarifa)

                        if(account_item.sricode == codigo and account_item.codigoporcentaje == codigoPorcentaje and account_item.tax_rate == float(tarifa)):
                            #Se retorna el item template encontrado ya que si contiene el impuesto
                            # al que se hace referencia
                            print("Se encontro la cuenta que coincide...")
                            print("Plantilla de impuesto de compra:")
                            print(item_template.name)
                            return account_item
                        

def evaluate_taxes(create_if_not_exists, codigo, codigoPorcentaje, tarifa):
    found_data_taxes_template = frappe.get_all('Purchase Taxes and Charges Template', fields = ['*'])
    #print(found_data_taxes_template)

    if(found_data_taxes_template):
        for item_template in found_data_taxes_template:
            
            #print(item_template.name)
            found_data_item_taxes_template = frappe.get_all('Purchase Taxes and Charges', fields = ['*'], filters={"parent": item_template.name})
            #print("found_data_item_taxes_template")
            #print(found_data_item_taxes_template)

            #Buscar Items de la Plantilla
            for tax_detail in found_data_item_taxes_template:
                #print("Cuenta de impuestos:", tax_detail.account_head)
                #print("Tasa de impuestos:", tax_detail.rate)
                
                #print("add_deduct_tax:", tax_detail.add_deduct_tax)
                #print("category:", tax_detail.category)
                #print("charge_type:", tax_detail.charge_type)

                if(tax_detail.category == 'Total' and tax_detail.add_deduct_tax == 'Add' and tax_detail.charge_type == 'On Net Total'):
                    found_account = frappe.get_all('Account', fields = ['*'], filters={"name": tax_detail.account_head})

                    #print(found_account)

                    for account_item in found_account:
                        print("name:", account_item.name)
                        print("sricode:", account_item.sricode)
                        print("codigoporcentaje:", account_item.codigoporcentaje)
                        print("tax_rate:", account_item.tax_rate)
                        print("------------------------")
                        print(codigo, codigoPorcentaje, tarifa)

                        if(account_item.sricode == codigo and account_item.codigoporcentaje == codigoPorcentaje and account_item.tax_rate == float(tarifa)):
                            #Se retorna el item template encontrado ya que si contiene el impuesto
                            # al que se hace referencia
                            print("Se encontro la cuenta que coincide...")
                            print("Plantilla de impuesto de compra:")
                            print(item_template.name)
                            return item_template

              

    #Crear
    #company : "RONALD STALIN CHONILLO VILLON"
    #name : "Ecuador Tax 15% (Compra) - RSCV"

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
            #print(child.text)
            #doc_comprobante = etree.fromstring(b'' + child.text)
            doc_comprobante = etree.fromstring(child.text.encode('utf-8'))
            #print(doc_comprobante)
            
            defaulProductGroup = 'Adquisiciones (DI)'
            defaultBrand = 'Sin Marca (DI)'

            #purchase_invoice_doc = frappe.get_last_doc("Purchase Invoice", doc_comprobante.find('infoTributaria').find('claveAcceso').text)
            found_purchase_invoice = frappe.get_all('Sales Invoice', filters={"numeroautorizacion": doc_comprobante.find('infoTributaria').find('claveAcceso').text}, fields = ['*'])
            
            if(found_purchase_invoice):               
                print('Registro exitente, se creará nuevo')
                reference_purchase_invoice = found_purchase_invoice[0]
                return
            
            #Se analizan los datos para crear los requeridos en caso de que no existan

            #Evaluar grupo de productos
            evaluate_product_group(True, defaulProductGroup)

            #Evaluar marca de productos
            evaluate_brand(True, defaultBrand)

            #Evaluar Proveedor
            evaluate_supplier(True, 
                              doc_comprobante.find('infoTributaria').find('ruc').text, 
                              doc_comprobante.find('infoTributaria').find('razonSocial').text, 
                              doc_comprobante.find('infoTributaria').find('nombreComercial').text, 
                              doc_comprobante.find('infoTributaria').find('dirMatriz').text)

           
            print('Registro nuevo')
            #new_client_script = frappe.get_doc(new_purchase_invoice)            
            #new_purchase_invoice_.base_grand_total = 0
            #new_purchase_invoice_.grand_total = 0
            #new_purchase_invoice_.items
            #new_purchase_invoice_.insert()
            #new_purchase_invoice_.db_set('sri_estado', 200)

            
            
            #print('fechaAutorizacion')
            #print(doc_root.find('fechaAutorizacion'))

            fechaAutorizacion = parser.parse(doc_root.find('fechaAutorizacion').text)
            #fechaAutorizacion = fecha_con_zona.replace(tzinfo=None)
            

            # print(doc_comprobante.find('infoTributaria').find('ambiente').text)
            # print(doc_comprobante.find('infoTributaria').find('tipoEmision').text)
            # print(doc_comprobante.find('infoTributaria').find('razonSocial').text)
            # print(doc_comprobante.find('infoTributaria').find('nombreComercial').text)
            # print(doc_comprobante.find('infoTributaria').find('ruc').text)
            # print(doc_comprobante.find('infoTributaria').find('claveAcceso').text)
            #---------------------------------------------------------------#
            # print(doc_comprobante.find('infoTributaria').find('codDoc').text)
            # print(doc_comprobante.find('infoTributaria').find('estab').text)
            # print(doc_comprobante.find('infoTributaria').find('ptoEmi').text)
            # print(doc_comprobante.find('infoTributaria').find('secuencial').text)
            # print(doc_comprobante.find('infoTributaria').find('dirMatriz').text)

            # print(doc_comprobante.find('infoFactura').find('fechaEmision').text)
            # print(doc_comprobante.find('infoFactura').find('dirEstablecimiento').text)
            # print(doc_comprobante.find('infoFactura').find('contribuyenteEspecial').text)
            # print(doc_comprobante.find('infoFactura').find('obligadoContabilidad').text)
            # print(doc_comprobante.find('infoFactura').find('tipoIdentificacionComprador').text)
            # print(doc_comprobante.find('infoFactura').find('razonSocialComprador').text)
            # print(doc_comprobante.find('infoFactura').find('identificacionComprador').text)
            # print(doc_comprobante.find('infoFactura').find('totalSinImpuestos').text)
            # print(doc_comprobante.find('infoFactura').find('totalDescuento').text)

            # print(doc_comprobante.find('infoFactura').find('totalConImpuestos').text)


            new_tax_items = []

            for totalConImpuestoItem in doc_comprobante.find('infoFactura').find('totalConImpuestos'):
                # print(totalConImpuestoItem.tag, totalConImpuestoItem.attrib)
                # print(totalConImpuestoItem.find('codigo').text)
                # print(totalConImpuestoItem.find('codigoPorcentaje').text)
                # print(totalConImpuestoItem.find('baseImponible').text)
                # print(totalConImpuestoItem.find('tarifa').text)
                # print(totalConImpuestoItem.find('valor').text)

                found_account = search_account_tax(True, 
                                    totalConImpuestoItem.find('codigo').text, 
                                    totalConImpuestoItem.find('codigoPorcentaje').text, 
                                    totalConImpuestoItem.find('tarifa').text)

                new_tax_item = {
                    "category" : "Total",
                    "add_deduct_tax" : "Add",
                    "charge_type" : "On Net Total",
                    "account_head" : found_account.name,
                    "description" : found_account.account_name + "@" + str(found_account.tax_rate),
                    "rate" : float(totalConImpuestoItem.find('tarifa').text),
                    "tax_amount" : float(totalConImpuestoItem.find('valor').text),
                    "tax_amount_after_discount_amount" : float(totalConImpuestoItem.find('valor').text),
                    "total" : float(totalConImpuestoItem.find('baseImponible').text) + float(totalConImpuestoItem.find('valor').text),
                    "base_tax_amount" : float(totalConImpuestoItem.find('valor').text)
                }
            
                new_tax_items.append(new_tax_item)

            # print(doc_comprobante.find('infoFactura').find('propina').text)
            # print(doc_comprobante.find('infoFactura').find('importeTotal').text)
            # print(doc_comprobante.find('infoFactura').find('moneda').text)

            for pagoItem in doc_comprobante.find('infoFactura').find('pagos'):
                print(pagoItem.tag, pagoItem.attrib)
                print(pagoItem.find('formaPago').text)
                print(pagoItem.find('total').text)
                print(pagoItem.find('plazo').text)
                print(pagoItem.find('unidadTiempo').text)
            
            
            new_items = []
            idx_item = 0
            for detalleItem in doc_comprobante.find('detalles'):
                # print(detalleItem.tag, detalleItem.attrib)
                # print(detalleItem.find('codigoPrincipal').text)
                # print(detalleItem.find('descripcion').text)
                # print(detalleItem.find('cantidad').text)
                # print(detalleItem.find('precioUnitario').text)
                # print(detalleItem.find('descuento').text)
                # print(detalleItem.find('precioTotalSinImpuesto').text)

                #Evaluar marca de productos                
                evaluate_item(True, 
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

                #print("idx_item _ PROCESS")
                #print(idx_item)
                #print(new_item)

                ++idx_item
                new_items.append(new_item)

                for detalleImpuestoItem in detalleItem.find('impuestos'):                    
                    purchase_taxes_and_charges_template = evaluate_taxes(True, 
                                                                         detalleImpuestoItem.find('codigo').text, 
                                                                         detalleImpuestoItem.find('codigoPorcentaje').text, 
                                                                         detalleImpuestoItem.find('tarifa').text)

                    if(not purchase_taxes_and_charges_template):
                        print("DEBE SALIR AQUI")
                        print("Los impuestos deben estar configurados en el sistema. Plantilla de impuesto de compras, códigos del SRI.")
                        pass

                    # print(detalleImpuestoItem.tag, detalleImpuestoItem.attrib)
                    # print(detalleImpuestoItem.find('codigo').text)
                    # print(detalleImpuestoItem.find('codigoPorcentaje').text)
                    # print(detalleImpuestoItem.find('tarifa').text)
                    # print(detalleImpuestoItem.find('baseImponible').text)
                    # print(detalleImpuestoItem.find('valor').text)
                    #Se agrega nuevo item                    

            infoAdicional = []
            for infoAdicionalItem in doc_comprobante.find('infoAdicional'):
                #print(infoAdicionalItem.tag, infoAdicionalItem.attrib)
                if(infoAdicionalItem.tag == 'campoAdicional'):
                    print(infoAdicionalItem.attrib['nombre'])
                    print(infoAdicionalItem.text)
                    infoAdicional.append({
                        "nombre": infoAdicionalItem.attrib['nombre'],
                        "valor": infoAdicionalItem.text
                    })

            #for child_comprobante in doc_comprobante:
                #print(child_comprobante.tag, child_comprobante.attrib)
            #    if(child_comprobante.tag == "infoTributaria"):
            #        print(child_comprobante.find('claveAcceso').text)            
            #f'{doc_data.secuencial:09d}'
            n_secuencial = int (doc_comprobante.find('infoTributaria').find('secuencial').text)
            
            docidsri = doc_comprobante.find('infoTributaria').find('estab').text + '-' + doc_comprobante.find('infoTributaria').find('ptoEmi').text + '-' + f'{n_secuencial:09d}'
            
            bill_date = parser.parse(doc_comprobante.find('infoFactura').find('fechaEmision').text)

            new_purchase_invoice_ = {
                "docstatus": 0,
			    "doctype": "Purchase Invoice",
                "numeroautorizacion": doc_comprobante.find('infoTributaria').find('claveAcceso').text,
                "numeroautorizacion" : doc_comprobante.find('infoTributaria').find('claveAcceso').text,
                "supplier" : doc_comprobante.find('infoTributaria').find('razonSocial').text,
                "secuencial" : doc_comprobante.find('infoTributaria').find('secuencial').text,
                "sri_ambiente" : int(doc_comprobante.find('infoTributaria').find('ambiente').text),
                "sri_estado" : 200,
                "sri_response" : 'AUTORIZADO',
                "docidsri": docidsri,
                "fechaautorizacion" : fechaAutorizacion.replace(tzinfo=None),
                "bill_no" : docidsri,
                "bill_date": bill_date.replace(tzinfo=None),
                "is_sri_imported": True,
                "items": new_items,
                "taxes" : new_tax_items,
                "infoadicional": infoAdicional
            }

            #print(new_purchase_invoice_)

            #Se crea nueva factura de compra importada
            reference_purchase_invoice = frappe.get_doc(new_purchase_invoice_)
            reference_purchase_invoice.insert()
            reference_purchase_invoice.save()

    if(remove_files):
        
        print(file_path)
        if os.path.exists(file_path):
            os.remove(file_path)