from __future__ import annotations

from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from .forms import InvoiceForm, InvoiceLineFormSet
from .models import Invoice, aggregate_line_totals


class InvoiceCreateView(View):
    template_name = "invoices/invoice_form.html"

    def get(self, request):
        form = InvoiceForm()
        formset = InvoiceLineFormSet()
        return render(request, self.template_name, {"form": form, "formset": formset})

    def post(self, request):
        form = InvoiceForm(request.POST)
        formset = InvoiceLineFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                invoice = form.save(commit=False)
                invoice.subtotal_amount = Decimal("0")
                invoice.discount_amount = Decimal("0")
                invoice.tax_amount = Decimal("0")
                invoice.total_amount = Decimal("0")
                invoice.save()
                formset.instance = invoice
                lines = formset.save()
                subtotal, discount, tax = aggregate_line_totals(invoice.lines.all())
                invoice.apply_totals(subtotal=subtotal, discount=discount, tax=tax)
                invoice.save(update_fields=[
                    "subtotal_amount",
                    "discount_amount",
                    "tax_amount",
                    "total_amount",
                ])
            messages.success(request, "Invoice created successfully.")
            return redirect(reverse("invoices:detail", args=[invoice.pk]))
        return render(request, self.template_name, {"form": form, "formset": formset})


class InvoiceDetailView(View):
    template_name = "invoices/invoice_detail.html"

    def get(self, request, pk: int):
        invoice = get_object_or_404(Invoice, pk=pk)
        return render(request, self.template_name, {"invoice": invoice})
