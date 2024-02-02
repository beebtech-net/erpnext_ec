from frappe import _

def get_data():
    return [
        {
            "label": _("ERPNext Ecuador"),
            "icon": "octicon octicon-book",
            "items": [
                {
                    "type": "doctype",
                    "name": "Sri Signature",
                    "label": _("Firmas"),
                    "description": _("Firmas electrónicas"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Sri Sequence",
                    "label": _("Secuenciales"),
                    "description": _("Secuenciales de documentos electrónicos"),
                    # Not displayed on dropdown list action but on page after click on module
                    "onboard": 1,
                }
            ]
        }
    ]