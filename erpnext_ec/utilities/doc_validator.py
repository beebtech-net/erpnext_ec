# Módulo para validación

import frappe
from erpnext_ec.utilities.doc_builder_tools import *
#from erpnext_ec.utilities.doc_render_tools import *

@frappe.whitelist()
def validate_sales_invoice(doc_name):
    #Esta validacion servira para saber si el documento contiene toda la informacion necesaria para el SRI
    result = {}
    header = []
    alerts = []
    documentIsReady = True

    doc = frappe.get_doc('Sales Invoice', doc_name)

    doctype_erpnext = 'Sales Invoice'
    typeDocSri = 'FAC'

    print(doctype_erpnext)
    print(doc)

    #sitenameVar = frappe.boot.sitename
    customer_email_id = ''

    customerApi = get_full_customer_sri(doc.customer)
    print(customerApi);

    customerAddress = None

    doc.paymentsItems = get_payments_sri(doc.name)    
    doc.pagos = build_pagos(doc.paymentsItems)
    paymentsApi = doc.paymentsItems

    if (paymentsApi):
        alerts.append({"index": 0, "description": "No se han definido datos de pago (solicitud de pago/entrada de pago)", "type":"error"})
        documentIsReady = False
   
    print(customerApi)
    if (customerApi['customer_tax_id'] == "" or customerApi['customer_tax_id'] == "9999999999"):
        alerts.append({"index": 0, "description": "Cédula/Ruc del cliente es ${customerApi.tax_id}", "type":"error"})

    print(customerAddress)
    if (customerAddress == None):            
        alerts.append({"index": 0, "description": "No se han definido datos de dirección del cliente", "type":"error"})
        documentIsReady = False    			

    if (customerAddress != None and (customerAddress.email_id == "" or customerAddress.email_id == None )):        
        alerts.append({"index": 0, "description": "No se ha definido Email del cliente", "type":"error"})
        documentIsReady = False    

    if (customerAddress != None):    
        customer_email_id = customerAddress.email_id    

    print(doc.estab)

    if (doc.estab == None or doc.estab == ''):
        alerts.append({"index": 0, "description": "Establecimiento incorrecto (${docApi.estab})", "type":"error"})
        documentIsReady = False
    
    else:    
        alerts.append({"index": 0, "description": "Establecimiento incorrecto (${docApi.estab})", "type":"error"}) #green
    

    print(doc.ptoemi);

    if (doc.ptoemi == None or doc.ptoemi == ''):        
        alerts.append({"index": 0, "description": "Punto de emisión incorrecto (${docApi.ptoemi})", "type":"error"})
        documentIsReady = False
    else:    
        alerts.append({"index": 0, "description": "Punto de emisión incorrecto (${docApi.ptoemi})", "type":"error"}) #green    

    header.append({"index": 0, "description": "Nombre cliente", "value":doc.customer_name})
    header.append({"index": 0, "description": "Tip.Doc. cliente", "value":customerApi['tipoIdentificacionComprador']})
    header.append({"index": 0, "description": "Cédula/RUC cliente", "value":customerApi['customer_tax_id']})
    header.append({"index": 0, "description": "Email cliente", "value":customer_email_id})

    result = {
        "header": header,
        "alerts": alerts,
        "doctype_erpnext": doctype_erpnext,
        "typeDocSri": "typeDocSri",
        "documentIsReady": documentIsReady
    }

    return result