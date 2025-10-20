from __future__ import annotations

from django.contrib import admin

from .models import Invoice, InvoiceLineItem


class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "customer", "status", "invoice_date", "total_amount")
    list_filter = ("status", "invoice_date")
    search_fields = ("invoice_number", "customer__first_name", "customer__last_name", "customer__email")
    inlines = [InvoiceLineItemInline]


@admin.register(InvoiceLineItem)
class InvoiceLineItemAdmin(admin.ModelAdmin):
    list_display = ("invoice", "description", "quantity", "unit_price", "line_subtotal")
    search_fields = ("invoice__invoice_number", "description")
