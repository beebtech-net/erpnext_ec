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

    frappe.enqueue(method= frappe.sendmail, queue = 'short', timeout = 60000, **email_args)

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