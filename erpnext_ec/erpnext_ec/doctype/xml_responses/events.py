import frappe
from erpnext_ec.utilities.email_tool import sendmail
from erpnext_ec.utilities.sri_ws import add_email_quote

def validate(doc, event):
    frappe.logger().info("validate")
    #frappe.logger().info(doc)

def on_update(doc, event):
    frappe.logger().info("on update")
    #frappe.logger().info(doc)

def after_insert(doc, event):

    #SE OMITE LA CREACION DE LA NOTA
    #note = frappe.get_doc({
    #    'doctype': 'Note',
    #    'title': f"{doc.name} Added",
    #    'public': True,
    #    'content': 'desc', #doc.description
    #})

    #note.insert()
    #frappe.db.commit()

    #frappe.msgprint(f"{note.title} has been created.")
    #sendmail(doc, recipients, msg, title, attachments = None)
    
    if(doc.sri_status == 'AUTORIZADO'):
    #if(True):
        #frappe.logger().info(doc)

        add_email_quote(doc.doc_ref, '', '', '', doc.tip_doc, doc.doc_type, "1")

        frappe.logger().info("Ready for send email -- FROM EVENT!!!!")
        frappe.logger().info("after_insert")
        frappe.logger().info(doc)
