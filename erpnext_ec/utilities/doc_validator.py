# Módulo para validación

import frappe
from erpnext_ec.utilities.doc_builder_tools import *
#from erpnext_ec.utilities.doc_render_tools import *

from erpnext_ec.utilities.doc_builder_fac import build_doc_fac 
from erpnext_ec.utilities.doc_builder_grs import build_doc_grs
from erpnext_ec.utilities.doc_builder_cre import build_doc_cre
from erpnext_ec.utilities.doc_builder_liq import build_doc_liq

@frappe.whitelist()
def validate_sales_invoice(doc_name):
    #Esta validacion servira para saber si el documento contiene toda la informacion necesaria para el SRI
    result = {}
    header = []
    alerts = []
    documentIsReady = True

    #doc = frappe.get_doc('Sales Invoice', doc_name)
    doc = build_doc_fac(doc_name)

    doctype_erpnext = 'Sales Invoice'
    typeDocSri = 'FAC'

    #print(doctype_erpnext)
    #print(doc)

    #sitenameVar = frappe.boot.sitename
    customer_email_id = ''

    #print(doc.paymentsItems)

    if(doc.is_return):
        typeDocSri='NCR'
        #Notas de crédito no requieren datos de pago
    else:
        if (not doc.paymentsItems):
            alerts.append({"index": 0, "description": "No se han definido datos de pago (solicitud de pago/entrada de pago)", "type":"error"})
            documentIsReady = False
    
    if (doc.tax_id == None):
        alerts.append({"index": 0, "description": "No se han definido ruc de compañia", "type":"error"})
        documentIsReady = False

    if (doc.customer_tax_id == "" or doc.customer_tax_id == "9999999999"):
        alerts.append({"index": 0, "description": f"Cédula/Ruc del cliente es {doc.tax_id}", "type":"error"})

    #print(doc.direccionComprador)
    if (doc.direccionComprador == None):            
        alerts.append({"index": 0, "description": "No se han definido datos de dirección del cliente", "type":"error"})
        documentIsReady = False

    if (doc.direccionComprador != None and (doc.customer_email_id == "" or doc.customer_email_id == None )):        
        alerts.append({"index": 0, "description": "No se ha definido Email del cliente", "type":"error"})
        documentIsReady = False

    print(doc.estab)

    if (doc.estab == None or doc.estab == ''):
        alerts.append({"index": 0, "description": f"Establecimiento incorrecto ({doc.estab})", "type":"error"})
        documentIsReady = False    
    else:    
        alerts.append({"index": 0, "description": f"Establecimiento correcto ({doc.estab})", "type":"info"}) #green

    #print(doc.ptoemi)

    if (doc.ptoemi == None or doc.ptoemi == ''):
        alerts.append({"index": 0, "description": f"Punto de emisión incorrecto ({doc.ptoemi})", "type":"error"})
        documentIsReady = False
    else:    
        alerts.append({"index": 0, "description": f"Punto de emisión correcto ({doc.ptoemi})", "type":"info"}) #green

    sri_environment = frappe.get_last_doc('Sri Environment', filters = { 'id': doc.ambiente })
    #print(sri_environment.name)
    #print(sri_environment.id)

    header.append({"index": 0, "description": "Ambiente", "value": sri_environment.description})
    header.append({"index": 1, "description": "Nombre cliente", "value":doc.customer_name})
    header.append({"index": 2, "description": "Tip.Doc. cliente", "value":doc.tipoIdentificacionComprador})
    header.append({"index": 3, "description": "Cédula/RUC cliente", "value":doc.customer_tax_id})
    header.append({"index": 4, "description": "Email cliente", "value":doc.customer_email_id})

    result = {
        "header": header,
        "alerts": alerts,
        "doctype_erpnext": doctype_erpnext,
        "typeDocSri": "typeDocSri",
        "documentIsReady": documentIsReady
    }

    return result

@frappe.whitelist()
def validate_delivery_note(doc_name):
    #Esta validacion servira para saber si el documento contiene toda la informacion necesaria para el SRI
    result = {}
    header = []
    alerts = []
    documentIsReady = True

    doc = build_doc_grs(doc_name)

    doctype_erpnext = 'Delivery Note'
    typeDocSri = 'GRS'

    print(doctype_erpnext)
    print(doc)

    #sitenameVar = frappe.boot.sitename
    customer_email_id = ''

    #customerApi = get_full_customer_sri(doc.customer)
    #print(customerApi);

    #doc.paymentsItems = get_payments_sri(doc.name)    
    #doc.pagos = build_pagos(doc.paymentsItems)
    #paymentsApi = doc.paymentsItems

    #if (doc.paymentsItems):
    #    alerts.append({"index": 0, "description": "No se han definido datos de pago (solicitud de pago/entrada de pago)", "type":"error"})
    #    documentIsReady = False
       
    if (doc.customer_tax_id == "" or doc.customer_tax_id == "9999999999"):
        alerts.append({"index": 0, "description": f"Cédula/Ruc del cliente es {doc.tax_id}", "type":"error"})

    print(doc.direccionComprador)
    if (doc.direccionComprador == None):            
        alerts.append({"index": 0, "description": "No se han definido datos de dirección del cliente", "type":"error"})
        documentIsReady = False    			

    if (doc.direccionComprador != None and (doc.contact_email == "" or doc.contact_email == None )):        
        alerts.append({"index": 0, "description": "No se ha definido Email del cliente", "type":"error"})
        documentIsReady = False    

    print(doc.estab)

    if (doc.estab == None or doc.estab == ''):
        alerts.append({"index": 0, "description": f"Establecimiento incorrecto ({doc.estab})", "type":"error"})
        documentIsReady = False    
    else:    
        alerts.append({"index": 0, "description": f"Establecimiento correcto ({doc.estab})", "type":"info"}) #green
    

    print(doc.ptoemi);

    if (doc.ptoemi == None or doc.ptoemi == ''):
        alerts.append({"index": 0, "description": f"Punto de emisión incorrecto ({doc.ptoemi})", "type":"error"})
        documentIsReady = False
    else:    
        alerts.append({"index": 0, "description": f"Punto de emisión correcto ({doc.ptoemi})", "type":"info"}) #green    

    header.append({"index": 0, "description": "Nombre cliente", "value":doc.customer_name})
    header.append({"index": 1, "description": "Tip.Doc. cliente", "value":doc.tipoIdentificacionComprador})
    header.append({"index": 2, "description": "Cédula/RUC cliente", "value":doc.customer_tax_id})
    header.append({"index": 3, "description": "Email cliente", "value":doc.contact_email})

    result = {
        "header": header,
        "alerts": alerts,
        "doctype_erpnext": doctype_erpnext,
        "typeDocSri": "typeDocSri",
        "documentIsReady": documentIsReady
    }

    return result


@frappe.whitelist()
def validate_purchase_whithold_sri_ec(doc_name):
    #Esta validacion servira para saber si el documento contiene toda la informacion necesaria para el SRI
    result = {}
    header = []
    alerts = []
    documentIsReady = True

    #doc = frappe.get_doc('Sales Invoice', doc_name)
    doc = build_doc_cre(doc_name)

    doctype_erpnext = 'Purchase Withholding Sri Ec'
    typeDocSri = 'CRE'

    #print(doctype_erpnext)
    #print(doc)

    #sitenameVar = frappe.boot.sitename
    customer_email_id = ''

    #print(doc.paymentsItems)
       
    if (doc.identificacionSujetoRetenido == "" or doc.identificacionSujetoRetenido == "9999999999"):
        alerts.append({"index": 0, "description": f"Cédula/Ruc del cliente es {doc.tax_id}", "type":"error"})

    #print(doc.direccionComprador)
    #if (doc.direccionComprador == None):
    #    alerts.append({"index": 0, "description": "No se han definido datos de dirección del cliente", "type":"error"})
    #    documentIsReady = False

    if (doc.direccionComprador != None and (doc.customer_email_id == "" or doc.customer_email_id == None )):        
        alerts.append({"index": 0, "description": "No se ha definido Email del cliente", "type":"error"})
        documentIsReady = False

    print(doc.estab)

    if (doc.estab == None or doc.estab == ''):
        alerts.append({"index": 0, "description": f"Establecimiento incorrecto ({doc.estab})", "type":"error"})
        documentIsReady = False    
    else:    
        alerts.append({"index": 0, "description": f"Establecimiento correcto ({doc.estab})", "type":"info"}) #green
    
    print(doc.ptoemi);

    if (doc.ptoemi == None or doc.ptoemi == ''):
        alerts.append({"index": 0, "description": f"Punto de emisión incorrecto ({doc.ptoemi})", "type":"error"})
        documentIsReady = False
    else:    
        alerts.append({"index": 0, "description": f"Punto de emisión correcto ({doc.ptoemi})", "type":"info"}) #green

    sri_environment = frappe.get_last_doc('Sri Environment', filters = { 'id': doc.ambiente })
    #print(sri_environment.name)
    #print(sri_environment.id)

    header.append({"index": 0, "description": "Ambiente", "value": sri_environment.description})
    header.append({"index": 1, "description": "Nombre proveedor", "value":doc.purchase_withholding_supplier})
    header.append({"index": 2, "description": "Tip.Doc. proveedor", "value":doc.tipoIdentificacionSujetoRetenido})
    header.append({"index": 3, "description": "Cédula/RUC proveedor", "value":doc.identificacionSujetoRetenido})
    header.append({"index": 3, "description": "Periodo Fiscal", "value":doc.identificacionSujetoRetenido})
    #header.append({"index": 4, "description": "Email cliente", "value":doc.customer_email_id})

    result = {
        "header": header,
        "alerts": alerts,
        "doctype_erpnext": doctype_erpnext,
        "typeDocSri": "typeDocSri",
        "documentIsReady": documentIsReady
    }

    return result

@frappe.whitelist()
def validate_purchase_receipt(doc_name):
    #Esta validacion servira para saber si el documento contiene toda la informacion necesaria para el SRI
    result = {}
    header = []
    alerts = []
    documentIsReady = True

    doc = build_doc_liq(doc_name)

    doctype_erpnext = 'Purchase Receipt'
    typeDocSri = 'LIQ'

    customer_email_id = ''
    
    if (doc.tax_id == None):
        alerts.append({"index": 0, "description": "No se han definido ruc de compañia", "type":"error"})
        documentIsReady = False

    if (doc.supplier_tax_id == "" or doc.supplier_tax_id == "9999999999"):
        alerts.append({"index": 0, "description": f"Cédula/Ruc del cliente es {doc.supplier_tax_id}", "type":"error"})

    #print(doc.direccionComprador)
    if (doc.direccionProveedor == None):
        alerts.append({"index": 0, "description": "No se han definido datos de dirección del proveedor", "type":"error"})
        documentIsReady = False

    if (doc.direccionProveedor != None and (doc.supplier_email_id == "" or doc.supplier_email_id == None )):        
        alerts.append({"index": 0, "description": "No se ha definido Email del proveedor", "type":"error"})
        documentIsReady = False

    print(doc.estab)

    if (doc.estab == None or doc.estab == ''):
        alerts.append({"index": 0, "description": f"Establecimiento incorrecto ({doc.estab})", "type":"error"})
        documentIsReady = False    
    else:    
        alerts.append({"index": 0, "description": f"Establecimiento correcto ({doc.estab})", "type":"info"}) #green

    #print(doc.ptoemi)

    if (doc.ptoemi == None or doc.ptoemi == ''):
        alerts.append({"index": 0, "description": f"Punto de emisión incorrecto ({doc.ptoemi})", "type":"error"})
        documentIsReady = False
    else:    
        alerts.append({"index": 0, "description": f"Punto de emisión correcto ({doc.ptoemi})", "type":"info"}) #green

    sri_environment = frappe.get_last_doc('Sri Environment', filters = { 'id': doc.ambiente })
    #print(sri_environment.name)
    #print(sri_environment.id)

    header.append({"index": 0, "description": "Ambiente", "value": sri_environment.description})
    header.append({"index": 1, "description": "Nombre proveedor", "value":doc.supplier_name})
    header.append({"index": 2, "description": "Tip.Doc. proveedor", "value":doc.tipoIdentificacionProveedor})
    header.append({"index": 3, "description": "Cédula/RUC proveedor", "value":doc.supplier_tax_id})
    header.append({"index": 4, "description": "Email proveedor", "value":doc.supplier_email_id})

    result = {
        "header": header,
        "alerts": alerts,
        "doctype_erpnext": doctype_erpnext,
        "typeDocSri": "typeDocSri",
        "documentIsReady": documentIsReady
    }

    return result