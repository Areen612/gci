from __future__ import annotations
from django.contrib import admin
from app.models import Invoice, InvoiceLineItem

class LineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 0
    autocomplete_fields = ("item",)
    readonly_fields = ("line_subtotal", "line_discount_total", "total_after_discount")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "customer",
        "status",
        "issue_date",
        "subtotal",
        "discount_total",
        "total_due",
    )

    list_filter = ("status", "issue_date", "payment_method")
    search_fields = ("invoice_number", "customer__name")
    autocomplete_fields = ("customer", "seller")
    inlines = [LineItemInline]

    ordering = ("-issue_date",)

    readonly_fields = (
        "subtotal",
        "discount_total",
        "total_due",
        "created_at",
        "updated_at",
        "xml",
        "qr_base64",
        "qr_image",
        "sequence_income_number",
    )