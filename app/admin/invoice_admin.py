from __future__ import annotations
from django.contrib import admin
from django.utils.html import format_html
from app.models import Invoice, InvoiceLineItem


class LineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 0
    autocomplete_fields = ("item",)

    readonly_fields = (
        "line_subtotal",
        "line_discount_total",
        "total_after_discount",
    )

    fields = (
        "item",
        "item_name",
        "quantity",
        "unit_price",
        "discount_amount",
        "line_subtotal",
        "line_discount_total",
        "total_after_discount",
    )

    classes = ("invoice-line-items",)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_locked:
            return self.fields
        return super().get_readonly_fields(request, obj)

    def has_add_permission(self, request, obj=None):
        if obj and obj.is_locked:
            return False
        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_locked:
            return False
        return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj and obj.is_locked:
            return False
        return super().has_change_permission(request, obj)

    class Media:
        css = {"all": ("css/admin_invoice_line_items.css",)}


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

    # These fields ALWAYS hidden from admin form
    hidden_fields = {"uuid", "xml", "qr_base64", "qr_image"}

    readonly_fields = (
        "subtotal",
        "discount_total",
        "total_due",
        "created_at",
        "updated_at",
        "qr_preview",
        "sequence_income_number",
    )

    # Replace clickable QR with a static preview
    def qr_preview(self, obj):
        if not obj.qr_image:
            return "-"
        return format_html(
            '<img src="{}" style="height:120px; border:1px solid #ddd; padding:4px; background:#fff;" />',
            obj.qr_image.url,
        )

    qr_preview.short_description = "QR Image"

    # Remove uuid/xml/qr_base64 from the form
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field in self.hidden_fields:
            if field in form.base_fields:
                form.base_fields.pop(field)
        return form


    #  Make all fields readonly when invoice is locked
    def get_readonly_fields(self, request, obj=None):
        base = list(super().get_readonly_fields(request, obj))

        if obj and obj.is_locked:
            # Add all model fields to readonly EXCEPT hidden ones
            model_fields = [f.name for f in obj._meta.fields if f.name not in self.hidden_fields]
            return tuple(sorted(set(base + model_fields)))

        return tuple(base)
    
    def get_inline_instances(self, request, obj=None):
        """
        Disable line item inlines when switching status from DRAFT → ISSUED,
        to prevent 'Issued invoices cannot be modified' validation errors.
        """
        if request.method == "POST":
            new_status = request.POST.get("status", None)

            if obj and obj.status == "DRAFT" and new_status == "ISSUED":
                # Completely skip inline validation & saving
                return []

        return super().get_inline_instances(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj and obj.is_locked and request.method not in ("GET", "HEAD", "OPTIONS"):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        # TODO: Issued invoices cannot be deleted. They must be voided, cancelled, or credited.
        return True
  
    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = self.get_object(request, object_id)

        if obj and obj.is_locked and request.method == "POST":
            # Instead of PermissionDenied, redirect safely
            from django.shortcuts import redirect
            self.message_user(request, "This invoice is issued and cannot be modified.", level='warning')
            return redirect(f"../{object_id}/change/")

        return super().change_view(request, object_id, form_url, extra_context)
    
    def render_change_form(self, request, context, *args, **kwargs):
        obj = context.get("original")

        if obj and obj.is_locked:
            context["show_save"] = False
            context["show_save_and_continue"] = False
            context["show_save_and_add_another"] = False
            context["show_delete"] = False

        return super().render_change_form(request, context, *args, **kwargs)