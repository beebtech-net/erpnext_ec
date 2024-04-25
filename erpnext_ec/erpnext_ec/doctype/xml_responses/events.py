import frappe
from erpnext_ec.utilities.email_tool import sendmail
from erpnext_ec.utilities.sri_ws import add_email_quote

def validate(doc, event):
    print("validate")
    print(doc)

def on_update(doc, event):
    print("on update")
    print(doc)

def after_insert(doc, event):

    note = frappe.get_doc({
        'doctype': 'Note',
        'title': f"{doc.name} Added",
        'public': True,
        'content': 'desc', #doc.description
    })

    note.insert()
    frappe.db.commit()
    #frappe.msgprint(f"{note.title} has been created.")

    #sendmail(doc, recipients, msg, title, attachments = None)
    
    add_email_quote(doc.name, '', '', '', doc.tip_doc, doc.doc_type, True)

    print("Ready for send email -- FROM EVENT!!!!")
    print("after_insert")
    print(doc)
