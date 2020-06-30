# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "sync_document"
app_title = "Sync Document"
app_publisher = "DAS"
app_description = " "
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = " "
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/sync_document/css/sync_document.css"
# app_include_js = "/assets/sync_document/js/sync_document.js"

# include js, css files in header of web template
# web_include_css = "/assets/sync_document/css/sync_document.css"
# web_include_js = "/assets/sync_document/js/sync_document.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "sync_document.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "sync_document.install.before_install"
# after_install = "sync_document.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sync_document.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Purchase Order": {
		"on_submit": "sync_document.sync_method.enqueue_sync_document_po",
	},
	"Sync Form":{
		"on_update":"sync_document.sync_method.enqueue_check_form"
	},
	"Purchase Receipt": {
		"on_submit": "sync_document.sync_method.sync_received_qty",
		"on_cancel": "sync_document.sync_method.cancel_sync_received_qty"
	},
	
 }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"sync_document.tasks.all"
# 	],
# 	"daily": [
# 		"sync_document.tasks.daily"
# 	],
# 	"hourly": [
# 		"sync_document.tasks.hourly"
# 	],
# 	"weekly": [
# 		"sync_document.tasks.weekly"
# 	]
# 	"monthly": [
# 		"sync_document.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "sync_document.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "sync_document.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "sync_document.task.get_dashboard_data"
# }

