# -*- coding: utf-8 -*-
# Copyright (c) 2015, erpx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from .frappeclient import FrappeClient
import json
import os
import requests
import subprocess
from frappe.utils.background_jobs import enqueue
from frappe.utils import get_site_name


@frappe.whitelist()
def enqueue_sync_document_po(doc, method):

# @frappe.whitelist()
# def manual_enqueue_sync_document_inv(document):


	# doc = frappe.get_doc("Purchase Order",document)

	if doc.amended_from:
		return
	list_server = frappe.db.sql(""" SELECT name FROM `tabSync Form` """,as_list=1)
	for row in list_server:
		sync_doc = row[0]
		if sync_doc:
			sync_form = frappe.get_doc("Sync Form", sync_doc)
			if sync_form.document_setting == "PO to SO" :
				customer_check = frappe.db.sql(""" SELECT sumber_supplier, tujuan_customer FROM `tabSync Form Customer Settings` WHERE parent = "{0}" """.format(sync_doc),as_list=1)
				if customer_check:
					for row_sync in customer_check:
						if row_sync[0] == doc.supplier:
							print("hola")
							enqueue("sync_document.sync_method.sync_po_so", doc=doc,sync_doc=sync_form,customer=row_sync[1])
							# sync_po_so(doc=doc,sync_doc=sync_form,customer=row_sync[1])



@frappe.whitelist()
def sync_po_so(doc,sync_doc,customer):
	
	clientroot = FrappeClient(sync_doc.server, "sync@mail.com", "asd123")
	# print(sync_doc.server)
	sumber = sync_doc.server.replace("http://","")


	pr_doc_items = []

	for row_item in doc.items:
		pr_doc_child = {}
		sumber_doc = frappe.get_doc("Item",row_item.item_code)
		if sumber_doc.stock_uom:
			uom_tujuan = clientroot.get_value("UOM", "name", {"name":sumber_doc.stock_uom})
			if not uom_tujuan:
				insert_uom = {"doctype": "UOM",
				"uom_name" : sumber_doc.stock_uom}
				clientroot.insert(insert_uom)
			
		if sumber_doc.item_group:
			uom_tujuan = clientroot.get_value("Item Group", "name", {"name":sumber_doc.item_group})
			if not uom_tujuan:
				insert_uom = {"doctype": "Item Group",
				"item_group_name" : sumber_doc.item_group,
				"parent_item_group" : "All Item Groups"
				}
				clientroot.insert(insert_uom)

		if sumber_doc.brand:
			uom_tujuan = clientroot.get_value("Brand", "name", {"name":sumber_doc.brand})
			if not uom_tujuan:
				insert_uom = {"doctype": "Brand",
				"brand" : sumber_doc.brand}
				clientroot.insert(insert_uom)

		docu_tujuan = clientroot.get_value("Item", "name", {"name":row_item.item_code})
		if not docu_tujuan:
			insert_doc = {"doctype": "Item",
		       "item_code": sumber_doc.item_code ,
		       "item_name": sumber_doc.item_name,
		       "item_group": sumber_doc.item_group,
		       "brand": sumber_doc.brand,
		       "description": sumber_doc.description,
		       "stock_uom":sumber_doc.stock_uom
		       }
			# create new record in ERPNext
			clientroot.insert(insert_doc)

		# warehouse = clientroot.get_value("Item", "default_warehouse", {"name": row_item.item_code})
		# ware = warehouse["default_warehouse"]

		pr_doc_child.update({
			"item_code" : row_item.item_code,
			"item_name" : row_item.item_name,
			"qty" : row_item.qty,
			"uom" : row_item.uom,
			"rate" : row_item.rate,
			# "warehouse": ware,
			"description": row_item.description,
			"conversion_factor" : row_item.conversion_factor,
			"purchase_order" : doc.name
			})


		pr_doc_items.append(pr_doc_child)
		# print(str(pr_doc_items))
	

	pr_doc = {}
	pr_doc.update({
		"doctype": "Sales Order",
		"customer" : customer,
		"transaction_date" : doc.transaction_date,
		"ync_from_document_name" : doc.name,
		"delivery_date" : doc.transaction_date,
		"sync_from" : str(frappe.utils.get_url()) ,
		"sync_from_document_name" : doc.name,
		"terms" : doc.terms,
		"items" : pr_doc_items,
		"additional_discount_percentage" : doc.additional_discount_percentage,
		"discount_amount" : doc.discount_amount})

	clientroot.insert(pr_doc)







@frappe.whitelist()
def sync_received_qty(doc,method):

# @frappe.whitelist()
# def sync_received_qty(document):

# 	doc = frappe.get_doc("Purchase Receipt",document)



	data_po  = frappe.db.sql(""" select distinct(preci.`purchase_order`) as `po` from `tabPurchase Receipt Item` preci
		where preci.`parent` = "{0}" """.format(doc.name), as_dict =1)

	tujuan_server =  frappe.db.sql("""  SELECT sf.`server` FROM `tabSync Form`sf, `tabSync Form Customer Settings` sfc
		WHERE sf.`name` = sfc.`parent`
		AND sfc.`sumber_supplier` = "{}"  """.format(doc.supplier), as_dict = 1)



	asal_server = str(frappe.utils.get_url())
	asal_server = asal_server.replace("http://","https://")

	# docu_so.save()


	for d in data_po:
		for t in tujuan_server :
			server = t.server.replace("https://","")
			server = server.replace("/","")
			enqueue("sync_document.sync_method.enqueue_sync_received_qty", tujuan_server=server,po=d.po,prec=doc.name, asal_server = asal_server)
			# enqueue_sync_received_qty(tujuan_server=server,po=d.po,prec=doc.name, asal_server = asal_server)

@frappe.whitelist()
def enqueue_sync_received_qty(tujuan_server,po, prec, asal_server):

	os.chdir("/home/frappe/frappe-bench")
	os.system(""" bench --site {0} execute sync_document_support.sync_method_support.update_received_qty --args "['{1}','{2}','{3}']" """.format(tujuan_server, po, prec, asal_server))




@frappe.whitelist()
def cancel_sync_received_qty(doc,method):



	data_po  = frappe.db.sql(""" select distinct(preci.`purchase_order`) as `po` from `tabPurchase Receipt Item` preci
		where preci.`parent` = "{0}" """.format(doc.name), as_dict =1)

	tujuan_server =  frappe.db.sql("""  SELECT sf.`server` FROM `tabSync Form`sf, `tabSync Form Customer Settings` sfc
		WHERE sf.`name` = sfc.`parent`
		AND sfc.`sumber_supplier` = "{}"  """.format(doc.supplier), as_dict = 1)


	asal_server = str(frappe.utils.get_url())
	asal_server = asal_server.replace("http://","https://")

	# docu_so.save()


	for d in data_po:
		for t in tujuan_server :
			server = t.server.replace("https://","")
			server = server.replace("/","")
			enqueue("sync_document.sync_method.enqueue_cancel_sync_received_qty", tujuan_server=server,po=d.po,prec=doc.name, asal_server = asal_server)

@frappe.whitelist()
def enqueue_cancel_sync_received_qty(tujuan_server,po, prec, asal_server):

	os.chdir("/home/frappe/frappe-bench")
	os.system(""" bench --site {0} execute sync_document_support.sync_method_support.cancel_update_received_qty --args "['{1}','{2}','{3}']" """.format(tujuan_server, po, prec, asal_server))










@frappe.whitelist()
def enqueue_check_form(doc, method):
	enqueue("sync_document.sync_method.check_form", doc=doc)
	# except:
	# 	frappe.throw("Cannot connect to destination server, please check your credentials. {0} {1} {2}".format(doc.name, doc.user_name, doc.password))

@frappe.whitelist()
def check_form(doc):
	# doc = frappe.get_doc("Sync Form","http://demo.crativate.com")
	try:
		clientroot = FrappeClient(doc.server, "sync@mail.com", "asd123")
		# clientroot = FrappeClient("http://demo.crativate.com","administrator","admin")
		frappe.db.sql(""" UPDATE `tabSync Form` SET message = "Success to Connect to Destination Server."  WHERE name = "{}" """.format(doc.name))

		# if doc.credit_to_account:
		# 	try:
		# 		accu_tujuan = clientroot.get_value("Account", "name", {"name":doc.credit_to_account})
		# 		if not accu_tujuan:
		# 			frappe.db.sql(""" UPDATE `tabSync Form` SET message = "Success to Connect to Destination Server. Account {} don't exists in Destination Server."  WHERE name = "{}" """.format(doc.credit_to_account, doc.name))
		# 	except:
		# 		frappe.db.sql(""" UPDATE `tabSync Form` SET message = "Success to Connect to Destination Server. Account {} don't exists in Destination Server."  WHERE name = "{}" """.format(doc.credit_to_account, doc.name))

		list_supplier = []
		for row in doc.supplier_list:
			try:
				docu_tujuan = clientroot.get_value("Customer", "name", {"name":row.tujuan_customer})
				if not docu_tujuan:
					frappe.db.sql(""" UPDATE `tabSync Form` SET message = "Success to Connect to Destination Server. Customer {} don't exists in Destination Server."  WHERE name = "{}" """.format(row.tujuan_customer, doc.name))
			except:
				frappe.db.sql(""" UPDATE `tabSync Form` SET message = "Success to Connect to Destination Server. Customer {} don't exists in Destination Server."  WHERE name = "{}" """.format(row.tujuan_customer, doc.name))
	except:
		frappe.db.sql(""" UPDATE `tabSync Form` SET message = "Failed to Connect to Destination Server, please check your credentials"  WHERE name = "{}" """.format(doc.name))







    




