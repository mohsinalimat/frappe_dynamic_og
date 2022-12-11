# Copyright (c) 2022, Hussain Nagaria and Contributors
# See license.txt

import frappe

from frappe.tests.utils import FrappeTestCase
from frappe.core.api.file import get_attached_images

class TestImageGeneration(FrappeTestCase):
	def setUp(self):
		# Disable any existing template
		frappe.db.set_value(
			"OG Image Template", {"is_enabled": True}, "is_enabled", False
		)

		# Create new test template
		self.test_og_template = frappe.get_doc(
			{
				"doctype": "OG Image Template",
				"for_doctype": "ToDo",
				"is_enabled": False,  # enable before using,
				"template_html": '<div style="width: 800px; background-color: #ff0000; display: flex;" ><h1>{{ doc.description }}</h1></div>',
			}
		)

	def test_does_not_generate_if_template_disabled(self):
		test_todo_doc = frappe.get_doc(
			{"doctype": "ToDo", "description": "Hello, Hussain!"}
		).insert()

		attached_images = get_attached_images("ToDo", [test_todo_doc.name])
		self.assertEqual(len(attached_images), 0)

	def test_image_attached_if_template_enabled(self):
		# enable the test template
		self.test_og_template.is_enabled = True
		self.test_og_template.save()

		# create a new todo doc
		test_todo_doc = frappe.get_doc(
			{"doctype": "ToDo", "description": "Bro, what's up?"}
		).insert()

		attached_images = get_attached_images("ToDo", [test_todo_doc.name])
		self.assertEqual(len(attached_images), 1)
		self.assertTrue(
			attached_images[test_todo_doc.name][0].startswith("/files/og_image_todo_")
		)

	def test_deletes_older_images_if_applicable(self):
		# enable the test template
		self.test_og_template.is_enabled = True
		self.test_og_template.save()

		# Turn Off automatic deletion
		frappe.db.set_single_value(
			"Frappe Dynamic OG Settings", "automatically_delete_old_images", 0
		)

		test_todo_doc = frappe.get_doc(
			{"doctype": "ToDo", "description": "Hello, Hussain!"}
		).insert()

		attached_images = get_attached_images("ToDo", [test_todo_doc.name])
		self.assertEqual(len(attached_images[test_todo_doc.name]), 1)

		# Update the document
		test_todo_doc.description = "Wednesday Addams"
		test_todo_doc.save()

		# 2 images should be present
		attached_images = get_attached_images("ToDo", [test_todo_doc.name])
		self.assertEqual(len(attached_images[test_todo_doc.name]), 2)

		# Turn on automatic deletion
		frappe.db.set_single_value(
			"Frappe Dynamic OG Settings", "automatically_delete_old_images", 1
		)

		# Create a new one
		test_todo_doc.description = "Sheldon, Raj, Howard and Leonard are my bros!"
		test_todo_doc.save()

		# Only the latest image must be attached (the other 2 get deleted)
		attached_images = get_attached_images("ToDo", [test_todo_doc.name])
		self.assertEqual(len(attached_images[test_todo_doc.name]), 1)
