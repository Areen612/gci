from __future__ import annotations

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.html import format_html

from app.models import Invoice, InvoiceLineItem
from app.models.invoice import STATUS_DRAFT, STATUS_ISSUED


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

    # change_form_template = "admin/app/invoice/change_form.html"

    # fields always hidden in the form
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

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "invoice_number",
                    "customer",
                    "seller",
                    "issue_date",
                    "due_date",
                    "status",
                    "payment_method",
                    "notes",
                )
            },
        ),
        (
            "Government Fields",
            {
                "classes": ("collapse",),
                "fields": (
                    "e_invoice_number",
                    "invoice_type",
                    "sequence_income_number",
                    "currency_name",
                ),
            },
        ),
        (
            "Totals",
            {
                "fields": (
                    "subtotal",
                    "discount_total",
                    "total_due",
                    "qr_preview",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    # pre-fill invoice number for new invoices
    def get_changeform_initial_data(self, request):
        return {"invoice_number": Invoice.generate_next_invoice_number()}

    # static QR image preview
    def qr_preview(self, obj):
        if not obj or not obj.qr_image:
            return "-"
        return format_html(
            '<img src="{}" style="height:120px; border:1px solid #ddd; '
            'padding:4px; background:#fff;" />',
            obj.qr_image.url,
        )

    qr_preview.short_description = "QR Image"

    # hide internal fields from admin form
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field in self.hidden_fields:
            if field in form.base_fields:
                form.base_fields.pop(field)
        return form

    # lock all fields when invoice is locked
    def get_readonly_fields(self, request, obj=None):
        base = list(super().get_readonly_fields(request, obj))
        if obj and obj.is_locked:
            model_fields = [
                f.name for f in obj._meta.fields if f.name not in self.hidden_fields
            ]
            return tuple(sorted(set(base + model_fields)))
        return tuple(base)

    def has_change_permission(self, request, obj=None):
        # allow GET/HEAD but block writes on locked invoices
        if obj and obj.is_locked and request.method not in ("GET", "HEAD", "OPTIONS"):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        # TODO: Issued invoices cannot be deleted. They must be voided, cancelled, or credited.
        return True
  
    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = self.get_object(request, object_id)
        if obj and obj.is_locked and request.method == "POST":
            self.message_user(
                request, "This invoice is issued and cannot be modified.", level="warning"
            )
            return redirect(f"../{object_id}/change/")
        return super().change_view(request, object_id, form_url, extra_context)

    # hide save buttons when locked (read-only mode)
    def render_change_form(self, request, context, *args, **kwargs):
        obj = context.get("original")
        if obj and obj.is_locked:
            context["show_save"] = False
            context["show_save_and_continue"] = False
            context["show_save_and_add_another"] = False
            context["show_delete"] = False
        return super().render_change_form(request, context, *args, **kwargs)

    # handle custom "Issue Invoice" button on change form
    def response_change(self, request, obj):
        if "_issue" in request.POST and obj.status == STATUS_DRAFT:
            obj.status = STATUS_ISSUED
            obj.save()
            self.message_user(request, "Invoice successfully issued.")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    # handle custom "Issue Invoice" button on add form
    def response_add(self, request, obj, post_url_continue=None):
        if "_issue" in request.POST:
            obj.status = STATUS_ISSUED
            obj.save()
            self.message_user(request, "Invoice successfully issued.")
            return HttpResponseRedirect(f"../{obj.pk}/change/")
        return super().response_add(request, obj, post_url_continue)