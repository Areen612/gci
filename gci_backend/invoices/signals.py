from __future__ import annotations

from decimal import Decimal

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Invoice, InvoiceLine, aggregate_line_totals


@receiver(post_save, sender=InvoiceLine)
@receiver(post_delete, sender=InvoiceLine)
def update_invoice_totals(sender, instance: InvoiceLine, **kwargs):
    invoice: Invoice = instance.invoice
    lines = invoice.lines.all()
    if not lines.exists():
        invoice.apply_totals(subtotal=Decimal("0"), discount=Decimal("0"), tax=Decimal("0"))
        Invoice.objects.filter(pk=invoice.pk).update(
            subtotal_amount=invoice.subtotal_amount,
            discount_amount=invoice.discount_amount,
            tax_amount=invoice.tax_amount,
            total_amount=invoice.total_amount,
        )
        return

    subtotal, discount, tax = aggregate_line_totals(lines)
    invoice.apply_totals(subtotal=subtotal, discount=discount, tax=tax)
    Invoice.objects.filter(pk=invoice.pk).update(
        subtotal_amount=invoice.subtotal_amount,
        discount_amount=invoice.discount_amount,
        tax_amount=invoice.tax_amount,
        total_amount=invoice.total_amount,
    )
