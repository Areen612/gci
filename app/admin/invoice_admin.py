from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from django.utils.html import format_html
from django.shortcuts import redirect

from app.models import Invoice, InvoiceLineItem


class LineItemInlineFormSet(BaseInlineFormSet):
    """
    Ensures that invoice cannot be saved without at least 1 line item.
    """
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        total_items = 0
        for form in self.forms:
            if not form.cleaned_data.get("DELETE", False) and form.cleaned_data.get("quantity"):
                total_items += 1

        if total_items == 0:
            raise ValidationError("Invoice must contain at least one line item.")


class LineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 1
    formset = LineItemInlineFormSet
    autocomplete_fields = ("item",)

    readonly_fields = (
        "line_subtotal",
        "line_discount_total",
        "total_after_discount",
    )

    fields = (
        "item",
        "description",
        "quantity",
        "unit_price",
        "discount_amount",
        "line_subtotal",
        "line_discount_total",
        "total_after_discount",
    )

    classes = ("invoice-line-items",)

    def get_readonly_fields(self, request, obj=None):
        return self.fields if obj and obj.is_locked else super().get_readonly_fields(request, obj)

    def has_add_permission(self, request, obj=None):
        return not (obj and obj.is_locked)

    def has_delete_permission(self, request, obj=None):
        return not (obj and obj.is_locked)

    def has_change_permission(self, request, obj=None):
        return not (obj and obj.is_locked)
    
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

    # performance & usability
    list_select_related = ("customer", "seller")
    date_hierarchy = "issue_date"

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
        (None, {
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
        }),
        ("Government Fields", {
            "classes": ("collapse",),
            "fields": (
                "e_invoice_number",
                "invoice_type",
                "sequence_income_number",
                "currency_name",
            )
        }),
        ("Totals", {
            "fields": (
                "subtotal",
                "discount_total",
                "total_due",
                "qr_preview",
                "created_at",
                "updated_at",
            )
        }),
    )

    def get_changeform_initial_data(self, request):
        return {"invoice_number": Invoice.generate_next_invoice_number()}

    def qr_preview(self, obj):
        if not obj or not obj.qr_image:
            return "-"
        return format_html(
            '<img src="{}" style="height:120px; border:1px solid #ddd; padding:4px; background:#fff;" />',
            obj.qr_image.url,
        )

    qr_preview.short_description = "QR Image"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field in self.hidden_fields:
            form.base_fields.pop(field, None)
        return form

    def get_readonly_fields(self, request, obj=None):
        base = list(super().get_readonly_fields(request, obj))
        if obj and obj.is_locked:
            model_fields = [
                f.name for f in obj._meta.fields if f.name not in self.hidden_fields
            ]
            return tuple(sorted(set(base + model_fields)))
        return tuple(base)

    def has_change_permission(self, request, obj=None):
        if obj and obj.is_locked and request.method not in ("GET", "HEAD"):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_locked:
            return False
        return super().has_delete_permission(request, obj)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = self.get_object(request, object_id)
        if obj and obj.is_locked and request.method == "POST":
            self.message_user(request, "This invoice is issued and cannot be modified.", level="warning")
            return redirect(f"../{object_id}/change/")
        return super().change_view(request, object_id, form_url, extra_context)