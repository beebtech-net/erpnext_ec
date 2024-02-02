import frappe

def sendmail(doc, recipients, msg, title, attachments = None):
    email_args = {
        'recipients': recipients,
        'message': msg,
        'subject': title,
        'reference_doctype': doc.doctype,
        'reference_name': doc.name,
    }

    if attachments: email_args['attachments'] = attachments

    frappe.queue(method= frappe.sendmail, queue = 'short', timeout = 300, **email_args)