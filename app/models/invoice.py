from __future__ import annotations
import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q, Sum

from .seller import Seller
from .item import Item
from .tax import Tax
from .discount import Discount
from .customer import Customer


STATUS_DRAFT = "draft"
STATUS_SENT = "sent"
STATUS_PAID = "paid"
STATUS_VOID = "void"

STATUS_CHOICES = [
    (STATUS_DRAFT, "Draft"),
    (STATUS_SENT, "Sent"),
    (STATUS_PAID, "Paid"),
    (STATUS_VOID, "Void"),
]
class Invoice(models.Model):
    """Represents a customer invoice."""

    PAYMENT_METHOD_CHOICES = [
        ("Cash", "Cash"),
        ("Card", "Card"),
        ("Mobile", "Mobile"),
        ("GiftCard", "Gift Card"),
        ("Account", "Account"),
    ]

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=100, unique=True)

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name="invoices")
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True)

    invoice_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # JOFotara API fields
    xml = models.TextField(null=True, blank=True)
    qr_base64 = models.TextField(null=True, blank=True)
    qr_image = models.ImageField(upload_to='invoices/qr/', null=True, blank=True)
    e_invoice_number = models.CharField(max_length=50, null=True, blank=True)
    invoice_type = models.CharField(max_length=50, null=True, blank=True)
    sequence_income_number = models.CharField(max_length=50, null=True, blank=True)
    currency_name = models.CharField(max_length=50, null=True, blank=True)
    total_before_discount = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    discount_value = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    notes = models.TextField(blank=True, max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-invoice_date"]
        constraints = [
            models.CheckConstraint(check=Q(subtotal__gte=0), name="subtotal_non_negative"),
            models.CheckConstraint(check=Q(tax_total__gte=0), name="tax_non_negative"),
            models.CheckConstraint(check=Q(discount_total__gte=0), name="discount_non_negative"),
            models.CheckConstraint(check=Q(total_due__gte=0), name="total_non_negative"),
            models.CheckConstraint(
                check=Q(status__in=[c[0] for c in STATUS_CHOICES]),
                name="valid_invoice_status",
            ),
        ]

    def clean(self) -> None:
        if self.status == self.STATUS_PAID and not self.payment_method:
            raise ValidationError("Payment method is required when invoice is marked as Paid.")

    def update_totals(self):
        """Recalculate subtotal, tax, discount, and total_due based on line items."""
        line_totals = self.line_items.aggregate(
            subtotal=Sum(F('line_subtotal')),
            tax_total=Sum(F('line_tax_total')),
            discount_total=Sum(F('line_discount_total'))
        )
        self.subtotal = line_totals.get('subtotal') or 0
        self.tax_total = line_totals.get('tax_total') or 0
        self.discount_total = line_totals.get('discount_total') or 0
        self.total_due = self.subtotal + self.tax_total - self.discount_total

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.update_totals()
        super().save(update_fields=['subtotal', 'tax_total', 'discount_total', 'total_due'])

    def __str__(self):
        return f"Invoice {self.invoice_number}"