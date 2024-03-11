# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from datetime import datetime
import frappe
from frappe import _
import json
from types import SimpleNamespace
import requests
from erpnext_ec.utilities.encryption import encrypt_string

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# from bson import json_util
# import json

import re

def build_comment(comments):
    str_comment = ''
    for comment in comments:
        # print(comment)
        str_comment = comment.get('content', '')
        str_comment = strip_html(str_comment)
        str_comment = normalize_string(str_comment)
        break  # Sale del bucle después de procesar el primer comentario
    
    # Aquí puedes manejar si str_comment está vacío después del bucle
    # if not str_comment:
    #     pass
    return str_comment

def strip_html(input_string):
    """Elimina todas las etiquetas HTML de una cadena."""
    return re.sub('<[^>]*>', '', input_string)

def normalize_string(source_str):
    """Normaliza una cadena eliminando caracteres especiales y espacios extra."""
    try:
        normalized_str = source_str.strip()
        normalized_str = re.sub('[^a-zA-Z0-9 ]+', '', normalized_str.normalize('NFD'))
    except Exception as e:
        print('Error: NormalizeString')
        print('Data: ' + source_str)
        # Aquí puedes manejar el error según tus necesidades
        normalized_str = source_str  # Considera devolver la cadena original o manejar de otra manera
    return normalized_str

def build_infoAdicional_sri(doc_name, customer_email_id, customer_phone):

    commentsApi = frappe.get_all('Comment', filters = { 'reference_name': doc_name }, fields='*' );
    # print('COMENTAAAAAARIOOOOOOSSSSSS')
    # print(commentsApi)

    strComment = build_comment(commentsApi)

    infoAdicionalData = "";
    infoAdicionalData = [{
                            "nombre":"email",
                            "valor": customer_email_id
                            },
                            {
                            "nombre":"tel.",
                            "valor": customer_phone
                            },
                            {
                            "nombre":"Doc. Ref.",
                            "valor":doc_name
                            },
                            {
                            "nombre":"Coment.",
                            "valor":strComment
                            }
                        ];

    return infoAdicionalData

def get_payments_sri(doc_name):
    sri_validated = ''
    sri_validated_message = ''
      
    #paymentsEntryApi = frappe.get_list('Payment Entry Reference', filters = { 'reference_name': doc_name }, 
    #                                   fields = ['name', 'reference_doctype','reference_name','payment_term','parent','parentfield','parenttype','allocated_amount'])
    
    paymentsEntryReferenceApi = frappe.get_all('Payment Entry Reference', fields='*', filters = { 'reference_name': doc_name })

    #print(paymentsEntryReferenceApi)

    if not paymentsEntryReferenceApi:
        #paymentsApi = frappe.get_list('Payment Request', filters = { 'reference_name': doc_name })
        paymentsApi = frappe.get_all('Payment Request', fields='*', filters = { 'reference_name': doc_name })
        # print(paymentsApi)

        if not paymentsApi and  not paymentsEntryReferenceApi:
            sri_validated = 'error'
            sri_validated_message += 'No se ha definido ni solicitud de pago ni entrada de pago-'
        else:
            return paymentsApi
    else:
        
        paymentResults = []

        for paymentEntryReference in paymentsEntryReferenceApi:
            paymentEntries = frappe.get_all('Payment Entry', fields='*', filters = { 'name': paymentEntryReference.parent })
            if(paymentEntries):
                for paymentEntry in paymentEntries:
                    paymentResults.append(paymentEntry)
            else:
                paymentResults.append(paymentEntryReference)        
        
        return paymentResults    
    return None

#devolver formaPago, total
def build_pagos(paymentResults):
    pagos = []
    for paymentEntry in paymentResults:
        mode_of_payment = frappe.get_all('Mode of Payment', fields='*', filters = { 'name': paymentEntry.mode_of_payment })
        if(mode_of_payment):
            pago_item = {}
            pago_item['formaPago'] = mode_of_payment[0].formapago
            pago_item['formaPagoDescripcion'] = mode_of_payment[0].name
            pago_item['total'] = paymentEntry.paid_amount
            pagos.append(pago_item)
    return pagos

def get_full_company_sri(def_company):
    # Variable de retorno
    compania_sri = {}

    # Obteniendo la compañía por defecto si def_company es None
    # def_company = def_company or frappe.defaults.get_user_default("Company")

    docs = frappe.get_all('Company', fields='*', filters={'name': def_company})
    #print(docs)
    
    if docs:
        doc = docs[0]
        compania_sri['nombreComercial'] = doc.nombrecomercial
        compania_sri['ruc'] = doc.tax_id
        compania_sri['obligadoContabilidad'] = doc.obligadocontabilidad
        compania_sri['contribuyenteRimpe'] = doc.contribuyenterimpe
        
        company_address_primary = None
        company_address_first = None

        din_link_api = frappe.get_all('Dynamic Link', fields='["name","parent","link_title"]',
                                                filters={'link_doctype': 'Company', 'parenttype': 'Address', 'link_name': def_company})
        #print(din_link_api)

        if din_link_api:
            found_primary = False
            for i, link in enumerate(din_link_api):
                company_address = frappe.get_all('Address', fields='*', filters={'name': link.parent})
                # print(company_address)

                if company_address:
                    if i == 0:
                        company_address_first = company_address[0]

                    if company_address[0].get('is_primary_address'):
                        found_primary = True
                        company_address_primary = company_address[0]
                        break

            if not found_primary and company_address_first:
                company_address_primary = company_address_first

        #print(company_address_primary)

        if company_address_primary:
            compania_sri['dirMatriz'] = company_address_primary.address_line1
        else:
            compania_sri['dirMatriz'] = ''

        #print(compania_sri)
        return compania_sri
    

def get_full_customer_sri(def_customer):
    # Variable de retorno
    customer_sri = {}

    # Obteniendo la compañía por defecto si def_company es None
    # def_company = def_company or frappe.defaults.get_user_default("Company")

    docs = frappe.get_all('Customer', fields='*', filters={'name': def_customer})    
    
    #print(docs)

    if docs:
        doc = docs[0]
        #print(doc)
        customer_sri['customer_tax_id'] = doc.tax_id
        if(doc.nombrecomercial):
            customer_sri['customer_name'] = doc.nombrecomercial
        else:
            customer_sri['customer_name'] = doc.name

        customer_sri['tipoIdentificacionComprador'] = doc.typeidtax
        customer_sri['customer_email_id']  = ''
        customer_sri['customer_phone']  = ''

        customer_address_primary = None
        customer_address_first = None

        din_link_api = frappe.get_all('Dynamic Link', fields='["name","parent","link_title"]',
                                                filters={'link_doctype': 'Customer', 'parenttype': 'Address', 'link_name': def_customer})
        # print('DIRECCCCCCCCCCIIIIIIIONNNNNNN CUSTOMMMMERRRR')
        # print(din_link_api)

        if din_link_api:
            found_primary = False
            for i, link in enumerate(din_link_api):
                customer_address = frappe.get_all('Address', fields='*', filters={'name': link.parent})
                #print(customer_address)

                if customer_address:
                    if i == 0:
                        customer_address_first = customer_address[0]

                    if customer_address[0].get('is_primary_address'):
                        found_primary = True
                        customer_address_primary = customer_address[0]
                        break

            if not found_primary and customer_address_first:
                customer_address_primary = customer_address_first
        else:
            #Sino se encuentra una dirección vinculada se busca una direccion primaria del cliente
            customer_address = frappe.get_all('Address', fields='*', filters={'name': docs[0].customer_primary_address})
            if customer_address:
                customer_address_primary = customer_address[0]
            else:
                print('---')
                
        if customer_address_primary:
            customer_sri['customer_email_id']  = customer_address_primary.email_id
            customer_sri['customer_phone']  = customer_address_primary.phone
            customer_sri['address_line1']  = customer_address_primary.address_line1
            customer_sri['address_line2']  = customer_address_primary.address_line2
            customer_sri['direccionComprador']  = customer_address_primary.address_line1 + ' ' + customer_address_primary.address_line2
        else:
            customer_sri['customer_email_id']  = ''
            customer_sri['customer_phone']  = ''
            customer_sri['address_line1']  = ''
            customer_sri['address_line2']  = ''
            customer_sri['direccionComprador']  = ''

        #print(compania_sri)
        return customer_sri

def get_full_supplier_sri(def_customer):
    # Variable de retorno
    supplier_sri = {}

    # Obteniendo la compañía por defecto si def_company es None
    # def_company = def_company or frappe.defaults.get_user_default("Company")

    docs = frappe.get_all('Supplier', fields='*', filters={'name': def_customer})    
    
    #print(docs)

    if docs:
        doc = docs[0]
        #print(doc)
        supplier_sri['supplier_tax_id'] = doc.tax_id
        supplier_sri['supplier_name'] = doc.nombrecomercial
        supplier_sri['tipoIdentificacionProveedor'] = doc.typeidtax
        supplier_sri['supplier_email_id']  = ''
        supplier_sri['supplier_phone']  = ''

        supplier_address_primary = None
        supplier_address_first = None

        din_link_api = frappe.get_all('Dynamic Link', fields='["name","parent","link_title"]',
                                                filters={'link_doctype': 'Supplier', 'parenttype': 'Address', 'link_name': def_customer})
        
        # print(din_link_api)

        if din_link_api:
            found_primary = False
            for i, link in enumerate(din_link_api):
                supplier_address = frappe.get_all('Address', fields='*', filters={'name': link.parent})
                #print(customer_address)

                if supplier_address:
                    if i == 0:
                        supplier_address_first = supplier_address[0]

                    if supplier_address[0].get('is_primary_address'):
                        found_primary = True
                        supplier_address_primary = supplier_address[0]
                        break

            if not found_primary and supplier_address_first:
                supplier_address_primary = supplier_address_first
        else:
            print (docs)
            #Sino se encuentra una dirección vinculada se busca una direccion primaria del proveedor
            supplier_address = frappe.get_all('Address', fields='*', filters={'name': docs[0].supplier_primary_address})
            if supplier_address:
                supplier_address_primary = supplier_address[0]
            else:
                print('---')
                
        if supplier_address_primary:
            supplier_sri['supplier_email_id']  = supplier_address_primary.email_id
            supplier_sri['supplier_phone']  = supplier_address_primary.phone
        else:
            supplier_sri['supplier_email_id']  = ''
            supplier_sri['supplier_phone']  = ''

        #print(compania_sri)
        return supplier_sri


def get_full_items(doc_name):    
    items = frappe.get_all('Sales Invoice Item',
                           filters={'parent': doc_name},
                           fields=['*']
                        #    fields=['item_code', 'item_name', 'rate', 'qty', 'amount']
                                       )

    return items

def get_full_items_delivery_note(doc_name):    
    items = frappe.get_all('Delivery Note Item',
                           filters={'parent': doc_name},
                           fields=['*']
                        #    fields=['item_code', 'item_name', 'rate', 'qty', 'amount']
                                       )

    return items

def get_full_taxes(doc_name):    
    
    impuestos = frappe.get_all('Sales Taxes and Charges', filters={'parent': doc_name}, fields=['*'])
    #    fields=['charge_type', 'account_head', 'tax_amount']
    
    for taxItem in impuestos:
        accountApi = frappe.get_doc('Account', taxItem.account_head)
        # print('CUENTAAAAAAAAAAAAA')
        # print(accountApi)
        #print(accountApi.sricode)
        #print(accountApi.sricodeper)
        #print(taxItem)

        if accountApi.sricode:
            taxItem.sricode =  int(accountApi.sricode)
              
        if accountApi.sricodeper:
            taxItem.codigoPorcentaje = int(accountApi.sricodeper)
            #taxItem.codigoPorcentaje = accountApi.sricodeper

    return impuestos

def get_address_by_name(link_name, primary_address, link_doctype):
    address_data = {}
    customer_address_primary = None
    customer_address_first = None

    din_link_api = frappe.get_all('Dynamic Link', fields='["name","parent","link_title"]',
                                                filters={'link_doctype': link_doctype, 'parenttype': 'Address', 'link_name': link_name})
        
    # print('DIRECCCCCCCCCCIIIIIIIONNNNNNN CUSTOMMMMERRRR')
    print(din_link_api)

    if din_link_api:
        found_primary = False
        for i, link in enumerate(din_link_api):
            customer_address = frappe.get_all('Address', fields='*', filters={'name': link.parent})
            #print(customer_address)

            if customer_address:
                if i == 0:
                    customer_address_first = customer_address[0]

                if customer_address[0].get('is_primary_address'):
                    found_primary = True
                    customer_address_primary = customer_address[0]
                    break

        if not found_primary and customer_address_first:
            customer_address_primary = customer_address_first
    else:
        #Sino se encuentra una dirección vinculada se busca una direccion primaria del cliente
        customer_address = frappe.get_all('Address', fields='*', filters={'name':  primary_address})
        if customer_address:
            customer_address_primary = customer_address[0]
        else:
            print('---')
            
    if customer_address_primary:
        address_data['email_id']  = customer_address_primary.email_id
        address_data['phone']  = customer_address_primary.phone
        address_data['address_line1']  = customer_address_primary.address_line1
        address_data['address_line2']  = customer_address_primary.address_line2
        address_data['direccion']  = customer_address_primary.address_line1 + ' ' + customer_address_primary.address_line2
    else:
        address_data['email_id']  = ''
        address_data['phone']  = ''
        address_data['address_line1']  = ''
        address_data['address_line2']  = ''
        address_data['direccion']  = ''
    
    return address_data


def get_invoice_by_link(link_name, link_doctype):
    invoice_data = {}   

    din_link_api = frappe.get_all('Dynamic Link', fields='["name","parent","link_title"]',
                                                filters={'link_doctype': link_doctype, 'parenttype': 'Sales Invoice', 'link_name': link_name})        
    
    print(din_link_api)

    if din_link_api:
        found_primary = False
        for i, link in enumerate(din_link_api):
            pass

def get_full_delivery_trips(doc):
    
    #print(doc['items'])

    doc_name = doc.name

    # document_links = frappe.get_all('Document link', filters={'parent': doc_name}, fields=['*'])
    # print("document_links")
    # print(document_links)

    delivery_trips = frappe.get_all('Delivery Trip', filters={'delivery_note': doc_name}, fields=['*'])
    #    fields=['charge_type', 'account_head', 'tax_amount']
    
    main_against_sales_invoice = ''
    numAutDocSustento = ''
    codEstabDestino = ''
    numDocSustento = ''
    # print(delivery_trips)
    for delivery_note_item in doc['items']:
        print("against_sales_invoice----")
        #print(doc.against_sales_invoice)
        #print(delivery_tripItem.against_sales_invoice)
        print(delivery_note_item.against_sales_invoice)
        main_against_sales_invoice = delivery_note_item.against_sales_invoice
        docs_si = frappe.get_all('Sales Invoice', filters={"name": main_against_sales_invoice}, fields = ['*'])        

        if docs_si:
            #doc = docs[0]
            print(docs_si[0])
            codEstabDestino = docs_si[0].estab
            #secuencial = docs_si[0].secuencial
            numAutDocSustento = docs_si[0].numeroautorizacion
            numDocSustento = docs_si[0].estab + '-' + docs_si[0].ptoemi + '-' + format(docs_si[0].secuencial, '09')
            print(numAutDocSustento)
            print(numDocSustento)


    for delivery_tripItem in delivery_trips:
        delivery_stops = frappe.get_all('Delivery Stop', filters={'parent': delivery_tripItem.name}, fields=['*'])
        
        for delivery_stops_item in delivery_stops:
            #dirDestinatario
            #numAutDocSustento
            #get_address_by_name(link_name, primary_address, link_doctype, parenttype)
            print(delivery_stops_item.address)
            primary_address = delivery_stops_item.address
            address_data = get_address_by_name(delivery_stops_item.address, primary_address, 'Customer')            
            #delivery_stops_item.customer
            print('address_data')
            print(address_data)
            delivery_stops_item.dirDestinatario = address_data['direccion']

            print(delivery_stops_item.name)
            print(delivery_stops_item.delivery_note)            

            delivery_stops_item.numAutDocSustento = numAutDocSustento
            delivery_stops_item.numDocSustento = numDocSustento
            delivery_stops_item.codEstabDestino = codEstabDestino

            pass

        #obtener datos del conductor y direccion de partida
        
        #obtener datos del vehículo

        # print('CUENTAAAAAAAAAAAAA')
        #print("delivery_trips")
        #print(delivery_tripItem)

        #print("delivery_stops")
        #print(delivery_stops)
        # print(accountApi.sricodeper)
        delivery_tripItem.delivery_stops = delivery_stops
        
        #delivery_trip_driver = frappe.get_last_doc('Driver', filters={'name': delivery_tripItem.driver})
        delivery_trip_driver = frappe.get_all('Driver', filters={'name': delivery_tripItem.driver}, fields=['*'])
        delivery_tripItem.trip_driver = delivery_trip_driver
        #print(delivery_trip_driver)
     
        #delivery_trip_vehicle = frappe.get_last_doc('Vehicle', filters={'name': delivery_tripItem.vehicle})
        delivery_trip_vehicle = frappe.get_all('Vehicle', filters={'name': delivery_tripItem.vehicle}, fields=['*'])
        delivery_tripItem.trip_vehicle = delivery_trip_vehicle
        #print(delivery_trip_vehicle)
        
    return delivery_trips


def get_full_taxes_withhold(doc_name):    
    
    impuestos = frappe.get_all('Purchase Taxes and Charges Ec', filters={'parent': doc_name}, fields=['*'])
    #    fields=['charge_type', 'account_head', 'tax_amount']
    
    for taxItem in impuestos:
        accountApi = frappe.get_doc('Account', taxItem.codigoRetencion)
        # print('CUENTAAAAAAAAAAAAA')
        # print(accountApi)
        # print(accountApi.sricode)
        # print(accountApi.sricodeper)

        if accountApi.sricode:
            taxItem.sricode =  int(accountApi.sricode)
              
        if accountApi.sricodeper:
            taxItem.codigoPorcentaje = int(accountApi.sricodeper)

    return impuestos