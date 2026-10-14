import frappe

def execute():
    if frappe.db.has_column("Account", "sricodeper"):
        frappe.db.sql("ALTER TABLE `tabAccount` DROP COLUMN `sricodeper`")
