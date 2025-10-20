from django.contrib import admin

from .models import Invoice, InvoiceLine


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "customer",
        "status",
        "invoice_date",
        "total_amount",
    )
    list_filter = ("status", "invoice_date")
    search_fields = ("invoice_number", "customer__first_name", "customer__last_name")
    inlines = [InvoiceLineInline]


@admin.register(InvoiceLine)
class InvoiceLineAdmin(admin.ModelAdmin):
    list_display = (
        "invoice",
        "description",
        "quantity",
        "unit_price",
        "tax_rate",
    )
    search_fields = ("description", "invoice__invoice_number")
    list_filter = ("tax_rate",)
