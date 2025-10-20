from __future__ import annotations

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.customers.models import Customer
from apps.inventory.models import InventoryItem


class Invoice(models.Model):
    """Represents a customer invoice."""

    class Status(models.TextChoices):
        DRAFT = "Draft", "Draft"
        ISSUED = "Issued", "Issued"
        PAID = "Paid", "Paid"
        CANCELLED = "Cancelled", "Cancelled"
        REFUNDED = "Refunded", "Refunded"

    class PaymentMethod(models.TextChoices):
        CASH = "Cash", "Cash"
        CARD = "Card", "Card"
        MOBILE = "Mobile", "Mobile"
        GIFTCARD = "GiftCard", "Gift Card"
        ACCOUNT = "Account", "Account"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="invoices")
    invoice_date = models.DateTimeField()
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    subtotal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
        blank=True,
    )
    notes = models.TextField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-invoice_date"]
        constraints = [
            models.CheckConstraint(check=Q(subtotal_amount__gte=0), name="subtotal_non_negative"),
            models.CheckConstraint(check=Q(tax_amount__gte=0), name="tax_non_negative"),
            models.CheckConstraint(check=Q(discount_amount__gte=0), name="discount_non_negative"),
            models.CheckConstraint(
                check=Q(discount_amount__lte=models.F("subtotal_amount")),
                name="discount_lte_subtotal",
            ),
            models.CheckConstraint(check=Q(total_amount__gte=0), name="total_non_negative"),
            models.CheckConstraint(
                check=Q(status__in=[choice for choice, _ in Status.choices]),
                name="valid_invoice_status",
            ),
        ]

    def clean(self) -> None:  # type: ignore[override]
        if self.status == self.Status.PAID and not self.payment_method:
            raise ValidationError("Payment method is required when invoice is marked as Paid.")

    def save(self, *args, **kwargs):  # type: ignore[override]
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Invoice {self.invoice_number}"


class InvoiceLineItem(models.Model):
    """Individual line items that compose an invoice."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="line_items")
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT, related_name="line_items")
    description = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(quantity__gt=0), name="line_quantity_positive"),
            models.CheckConstraint(check=Q(unit_price__gte=0), name="line_unit_price_non_negative"),
            models.CheckConstraint(check=Q(line_subtotal__gte=0), name="line_subtotal_non_negative"),
            models.CheckConstraint(check=Q(tax_amount__gte=0), name="line_tax_non_negative"),
            models.CheckConstraint(check=Q(discount_amount__gte=0), name="line_discount_non_negative"),
            models.CheckConstraint(
                check=Q(discount_amount__lte=models.F("line_subtotal")),
                name="line_discount_lte_subtotal",
            ),
        ]

    def clean(self) -> None:  # type: ignore[override]
        if self.discount_amount > self.line_subtotal:
            raise ValidationError("Discount amount cannot exceed the line subtotal.")

    def save(self, *args, **kwargs):  # type: ignore[override]
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.description} x {self.quantity}"
