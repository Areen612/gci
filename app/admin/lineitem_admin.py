from __future__ import annotations
from django.contrib import admin
from app.models import InvoiceLineItem

@admin.register(InvoiceLineItem)
class InvoiceLineItemAdmin(admin.ModelAdmin):
    list_display = ("invoice", "item", "quantity", "unit_price", "total_after_discount")
    list_filter = ("item",)
    search_fields = ("invoice__invoice_number", "item__name")

