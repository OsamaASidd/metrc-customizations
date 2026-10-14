app_name = "metrc_customizations"
app_title = "Metrc Customizations"
app_publisher = "alltechvirtual.com"
app_description = "Metrc integration: tags, licences, config and Metrc fields"
app_email = "osama.ahmad@alltechvirtual.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["erpnext"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "metrc_customizations",
# 		"logo": "/assets/metrc_customizations/logo.png",
# 		"title": "Metrc Customizations",
# 		"route": "/metrc_customizations",
# 		"has_permission": "metrc_customizations.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/metrc_customizations/css/metrc_customizations.css"
app_include_js = [
    # Shared Muid (Metrc Tag) Link-query filter, keyed off the row's warehouse
    # License. The Stock Entry / Purchase Receipt / Purchase Invoice / Delivery
    # Note / Sales Invoice form scripts (cannabis_management) call
    # cannabis_management.metric_tag.filter_by_warehouse() from here.
    # NOTE: no build-hash on these paths, so bump ?v= on every content change
    # or browsers/proxies keep serving the old file.
    "/assets/metrc_customizations/js/metric_tag_query.js?v=4",
    # Scan-to-select for Metrc Tag: patches erpnext's shared BarcodeScanner so
    # scanning a tag's Tag Code/MUID opens a picker of what is in stock under it.
    "/assets/metrc_customizations/js/metric_tag_scan.js?v=3",
]

# include js, css files in header of web template
# web_include_css = "/assets/metrc_customizations/css/metrc_customizations.css"
# web_include_js = "/assets/metrc_customizations/js/metrc_customizations.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "metrc_customizations/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "metrc_customizations/public/icons.svg"

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

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "metrc_customizations.utils.jinja_methods",
# 	"filters": "metrc_customizations.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "metrc_customizations.install.before_install"
# after_install = "metrc_customizations.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "metrc_customizations.uninstall.before_uninstall"
# after_uninstall = "metrc_customizations.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "metrc_customizations.utils.before_app_install"
# after_app_install = "metrc_customizations.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "metrc_customizations.utils.before_app_uninstall"
# after_app_uninstall = "metrc_customizations.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "metrc_customizations.notifications.get_notification_config"

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

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"metrc_customizations.tasks.all"
# 	],
# 	"daily": [
# 		"metrc_customizations.tasks.daily"
# 	],
# 	"hourly": [
# 		"metrc_customizations.tasks.hourly"
# 	],
# 	"weekly": [
# 		"metrc_customizations.tasks.weekly"
# 	],
# 	"monthly": [
# 		"metrc_customizations.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "metrc_customizations.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "metrc_customizations.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "metrc_customizations.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["metrc_customizations.utils.before_request"]
# after_request = ["metrc_customizations.utils.after_request"]

# Job Events
# ----------
# before_job = ["metrc_customizations.utils.before_job"]
# after_job = ["metrc_customizations.utils.after_job"]

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
# 	"metrc_customizations.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []


# Every Metrc custom field / property setter carries module "Metrc Customizations".
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "Metrc Customizations"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "Metrc Customizations"]]},
]
