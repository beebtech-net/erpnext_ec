import frappe

def sendmail(doc, recipients, title, msg_template, attachments = None):    
    #print(attachments)

    email_args = {
        'recipients': recipients,
        'message': msg_template,
        'subject': title,
        'reference_doctype': doc.doctype,
        'reference_name': doc.name,
        'attachments': attachments
        #'template': 'Factura SRI Body'
    }

    #if attachments: email_args['attachments'] = attachments

    result_queue = frappe.enqueue(method= frappe.sendmail, queue = 'short', timeout = 30000, delayed=False, **email_args)
    print(result_queue)

    # frappe.sendmail(
    # recipients=recipients,
    # subject=frappe._('Birthday Reminder'),
    # template='birthday_reminder',
    # args=dict(
    #     reminder_text=reminder_text,
    #     birthday_persons=birthday_persons,
    #     message=message,
    # ),
    # header=_('Birthday Reminder 🎂')
    #)