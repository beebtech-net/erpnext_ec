from frappe import __version__ as frappe_version

app_name = "erpnext_ec"
app_title = "ERPNext Ec"
app_publisher = "BeebTech"
app_description = "Erpnext Ecuador"
app_email = "ronald.chonillo@gmail.com"
app_license = "mit"
required_apps = [
    'erpnext'
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/erpnext_ec/css/erpnext_ec.css"
# app_include_js = "/assets/erpnext_ec/js/erpnext_ec.js"

app_include_js = [
    "/assets/erpnext_ec/js/sri_custom.js",
    "/assets/erpnext_ec/js/sales_invoice_tools.js",
    "/assets/erpnext_ec/js/delivery_note_tools.js",
    "/assets/erpnext_ec/js/withholding_tools.js",
    "/assets/erpnext_ec/js/frappe_sri_ui_tools.js",
    #"/assets/erpnext_ec/js/erpnext_ec.bundle.js",

    "/assets/erpnext_ec/js/libs/jsonTree/jsonTree.js",
    "/assets/erpnext_ec/js/libs/monthpicker/jquery.ui.monthpicker.min.js",
    "/assets/erpnext_ec/js/utils/desk.custom.js",
]

app_include_css = [
    "/assets/erpnext_ec/js/libs/jsonTree/jsonTree.css",
    "/assets/erpnext_ec/js/libs/monthpicker/qunit.min.css",
    "/assets/erpnext_ec/js/libs/monthpicker/jquery-ui.css",
]


# include js, css files in header of web template
# web_include_css = "/assets/erpnext_ec/css/erpnext_ec.css"
# web_include_js = "/assets/erpnext_ec/js/erpnext_ec.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "erpnext_ec/public/scss/website"

# include js, css files in header of web form
#webform_include_js = {"Sales Invoice": "/assets/erpnext_ec/js/sales_invoice_form.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Sales Invoice" : "public/js/overrides/sales_invoice_form_sri.js",
    "Delivery Note" : "public/js/overrides/delivery_note_form_sri.js",   
    
    }
doctype_list_js = {
    "Sales Invoice" : "public/js/overrides/sales_invoice_list_sri.js",
    "Purchase Invoice" : "public/js/overrides/purchase_invoice_list_sri.js",
    "Delivery Note" : "public/js/overrides/delivery_note_list_sri.js",


    "Print Format" : "public/js/overrides/print_format_list_sri.js",
    "Account" : "public/js/overrides/account_list_sri.js",
    }
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "erpnext_ec/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

is_frappe_above_v14 = int(frappe_version.split('.')[0]) > 14
is_frappe_above_v13 = int(frappe_version.split('.')[0]) > 13
is_frappe_above_v12 = int(frappe_version.split('.')[0]) > 12

frappe_version_int = int(frappe_version.split('.')[0])

#print(is_frappe_above_v13)
#print(is_frappe_above_v12)
#print(is_frappe_above_v14)

# Jinja
# ----------
#if(frappe_version_int == 13):
#if(True):
    #Frappe >=14
    # add methods and filters to jinja environment
#jinja = {
    #"methods": "erpnext_ec.utils.jinja_methods",
#    "methods": [
#                "erpnext_ec.utilities.doc_builder_fac",
#                "erpnext_ec.utilities.doc_builder_cre",
#                "erpnext_ec.utilities.doc_builder_grs",
#                ]
    #"filters": "erpnext_ec.utils.jinja_filters"
#}

#if(frappe_version_int > 13):
#if(False):
#from erpnext_ec.utilities.doc_builder_fac import build_doc_fac 
# from erpnext_ec.utilities.doc_builder_cre import build_doc_cre

#Frappe <=13
jenv = {
     "methods": [
         "build_doc_fac:erpnext_ec.utilities.doc_builder_fac.build_doc_fac",
         "build_doc_fac_with_images:erpnext_ec.utilities.doc_builder_fac.build_doc_fac_with_images",
         #"build_doc_cre:erpnext_ec.utilities.doc_builder_cre.build_doc_cre"
         #"build_doc_cre_with_images:erpnext_ec.utilities.doc_builder_cre.build_doc_cre_with_images"
     ],
     "filters": [
     ]
}

def jenv_customizations(jenv):
    #    jenv.globals['build_doc_fac'] = build_doc_fac
    print ("no usado")


# Installation
# ------------

before_install = "erpnext_ec.install.before_install"
#after_install = ["erpnext_ec.install.after_install","erpnext_ec.patches.client_scripts.execute"]
after_install = ["erpnext_ec.install.after_install"]

# Uninstallation
# ------------

# before_uninstall = "erpnext_ec.uninstall.before_uninstall"
# after_uninstall = "erpnext_ec.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "erpnext_ec.utils.before_app_install"
# after_app_install = "erpnext_ec.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "erpnext_ec.utils.before_app_uninstall"
# after_app_uninstall = "erpnext_ec.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "erpnext_ec.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

#override_doctype_class = {
# 	"Sales Invoices": "erpnext_ec.overrides.CustomToDo"
#}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Xml Responses": {
        "validate": "erpnext_ec.erpnext_ec.doctype.xml_responses.events.validate",
	    "on_update": "erpnext_ec.erpnext_ec.doctype.xml_responses.events.on_update",
        "after_insert": "erpnext_ec.erpnext_ec.doctype.xml_responses.events.after_insert",
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"erpnext_ec.tasks.all"
# 	],
# 	"daily": [
# 		"erpnext_ec.tasks.daily"
# 	],
# 	"hourly": [
# 		"erpnext_ec.tasks.hourly"
# 	],
# 	"weekly": [
# 		"erpnext_ec.tasks.weekly"
# 	],
# 	"monthly": [
# 		"erpnext_ec.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "erpnext_ec.install.before_tests"

# Overriding Methods
# ------------------------------
#
#override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "erpnext_ec.event.get_events"
#  "erpnext_ec.utilities.sri_ws.send_doc": "erpnext_ec.utilities.sri_ws.send_doc"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "erpnext_ec.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["erpnext_ec.utils.before_request"]
# after_request = ["erpnext_ec.utils.after_request"]

# Job Events
# ----------
# before_job = ["erpnext_ec.utils.before_job"]
# after_job = ["erpnext_ec.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"erpnext_ec.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

#app_include_js = [
#    'better_list_view.bundle.js'
#] if is_frappe_above_v13 else ([
#    '/assets/frappe_better_list_view/js/better_list_view.js'
#] if is_frappe_above_v12 else [
#    '/assets/frappe_better_list_view/js/better_list_view_v12.js'
#])

get_translated_dict = {
	("doctype", "Global Defaults"): "frappe.geo.country_info.get_translated_dict"
}