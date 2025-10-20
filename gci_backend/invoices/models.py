from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from gci_backend.core.models import TimeStampedModel
from gci_backend.customers.models import Customer
from gci_backend.inventory.models import Product


class Invoice(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        CARD = "card", "Card"
        MOBILE = "mobile", "Mobile"
        GIFT_CARD = "gift_card", "Gift card"
        ACCOUNT = "account", "On account"

    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name="invoices"
    )
    invoice_number = models.CharField(max_length=32, unique=True)
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.DRAFT
    )
    invoice_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    subtotal_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        default=Decimal("0"),
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        default=Decimal("0"),
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        default=Decimal("0"),
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        default=Decimal("0"),
    )
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, blank=True
    )
    notes = models.TextField(blank=True)

    ALLOWED_STATUS_TRANSITIONS: dict[str, set[str]] = {
        Status.DRAFT: {Status.ISSUED, Status.CANCELLED},
        Status.ISSUED: {Status.PAID, Status.CANCELLED},
        Status.PAID: {Status.REFUNDED},
        Status.CANCELLED: set(),
        Status.REFUNDED: set(),
    }

    class Meta:
        ordering = ["-invoice_date", "invoice_number"]

    def clean(self) -> None:
        errors: dict[str, str] = {}
        if self.due_date and self.due_date < self.invoice_date:
            errors["due_date"] = "Due date cannot be earlier than the invoice date."
        if self.discount_amount > self.subtotal_amount:
            errors["discount_amount"] = "Discount cannot exceed subtotal."
        expected_total = self.subtotal_amount - self.discount_amount + self.tax_amount
        if self.total_amount != expected_total.quantize(Decimal("0.01")):
            errors["total_amount"] = "Total must equal subtotal - discount + tax."
        if self.status == self.Status.PAID and not self.payment_method:
            errors["payment_method"] = "Payment method is required when marking an invoice as paid."
        if self.status == self.Status.PAID and self.total_amount <= 0:
            errors["total_amount"] = "Paid invoices must have a positive total."

        if self.pk:
            previous = Invoice.objects.get(pk=self.pk)
            if previous.status != self.status:
                allowed = self.ALLOWED_STATUS_TRANSITIONS.get(previous.status, set())
                if self.status not in allowed:
                    errors["status"] = (
                        f"Cannot change status from {previous.get_status_display()} "
                        f"to {self.get_status_display()}."
                    )

        if errors:
            raise ValidationError(errors)

    def apply_totals(self, *, subtotal: Decimal, discount: Decimal, tax: Decimal) -> None:
        self.subtotal_amount = subtotal
        self.discount_amount = discount
        self.tax_amount = tax
        self.total_amount = (subtotal - discount + tax).quantize(Decimal("0.01"))

    def __str__(self) -> str:
        return f"Invoice {self.invoice_number}"


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="lines"
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="invoice_lines"
    )
    description = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))]
    )
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal("0"))]
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        default=Decimal("0"),
    )
    line_subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        default=Decimal("0"),
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        default=Decimal("0"),
    )

    class Meta:
        ordering = ["pk"]

    def clean(self) -> None:
        errors: dict[str, str] = {}
        subtotal = self.quantity * self.unit_price
        if self.discount_amount > subtotal:
            errors["discount_amount"] = "Discount cannot exceed line subtotal."
        if errors:
            raise ValidationError(errors)

    def calculate_amounts(self) -> tuple[Decimal, Decimal]:
        subtotal = (self.quantity * self.unit_price).quantize(Decimal("0.01"))
        taxable_base = subtotal - self.discount_amount
        tax_amount = (taxable_base * (self.tax_rate / Decimal("100"))).quantize(
            Decimal("0.01")
        )
        return subtotal, tax_amount

    def save(self, *args, **kwargs):
        self.full_clean()
        subtotal, tax_amount = self.calculate_amounts()
        self.line_subtotal = subtotal
        self.tax_amount = tax_amount
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.description} x {self.quantity}"


def aggregate_line_totals(lines: Iterable[InvoiceLine]) -> tuple[Decimal, Decimal, Decimal]:
    subtotal = Decimal("0")
    discount = Decimal("0")
    tax = Decimal("0")
    for line in lines:
        subtotal += line.line_subtotal
        discount += line.discount_amount
        tax += line.tax_amount
    return subtotal.quantize(Decimal("0.01")), discount.quantize(Decimal("0.01")), tax.quantize(Decimal("0.01"))
