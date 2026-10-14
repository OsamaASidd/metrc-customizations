"""Delivery Note <-> Metrc Package: the Source Package's quantity goes down by
the row's quantity (Movement Log: Out); cancelling puts it back."""

from metrc_customizations import packages


def validate(doc, method=None):
	if doc.is_return:
		return
	used = {}
	for row in doc.items:
		if row.get("custom_source_package"):
			packages.validate_source(row, row.custom_source_package, row.stock_qty, used)


def on_submit(doc, method=None):
	if doc.is_return:
		return
	for row in doc.items:
		if row.get("custom_source_package"):
			packages.consume(doc, row, row.custom_source_package, row.stock_qty)
			packages.stamp_ledger(doc, row, row.custom_source_package, "out")


def on_cancel(doc, method=None):
	if doc.is_return:
		return
	for row in doc.items:
		if row.get("custom_source_package"):
			packages.restore(doc, row, row.custom_source_package)
