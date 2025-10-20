from __future__ import annotations

from django import forms
from django.forms import inlineformset_factory

from .models import Invoice, InvoiceLine


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "customer",
            "invoice_number",
            "status",
            "invoice_date",
            "due_date",
            "payment_method",
            "notes",
        ]

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class InvoiceLineForm(forms.ModelForm):
    class Meta:
        model = InvoiceLine
        fields = [
            "product",
            "description",
            "quantity",
            "unit_price",
            "tax_rate",
            "discount_amount",
        ]


InvoiceLineFormSet = inlineformset_factory(
    Invoice,
    InvoiceLine,
    form=InvoiceLineForm,
    extra=1,
    can_delete=False,
)
