from __future__ import annotations
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q, Sum

from .seller import Seller
from .customer import Customer


STATUS_DRAFT = "DRAFT"
STATUS_ISSUED = "ISSUED"
STATUS_UNPAID = "UNPAID"
STATUS_DECLINED = "DECLINED"

STATUS_CHOICES = [
    (STATUS_DRAFT, "Draft"),
    (STATUS_ISSUED, "Issued"),
    (STATUS_UNPAID, "Unpaid"),
    (STATUS_DECLINED, "Declined"),
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

    issue_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    total_due = models.DecimalField(max_digits=12, decimal_places=3, default=0)

    # JOFotara API fields
    xml = models.TextField(null=True, blank=True)
    qr_base64 = models.TextField(null=True, blank=True)
    qr_image = models.ImageField(upload_to='invoices/qr/', null=True, blank=True)
    e_invoice_number = models.CharField(max_length=50, null=True, blank=True)
    invoice_type = models.CharField(max_length=50, null=True, blank=True)
    sequence_income_number = models.CharField(max_length=50, null=True, blank=True)
    currency_name = models.CharField(max_length=50, null=True, blank=True, default="JOD")
    notes = models.TextField(blank=True, max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issue_date"]
        constraints = [
            models.CheckConstraint(check=Q(subtotal__gte=0), name="subtotal_non_negative"),
            models.CheckConstraint(check=Q(discount_total__gte=0), name="discount_non_negative"),
            models.CheckConstraint(check=Q(total_due__gte=0), name="total_non_negative"),
            models.CheckConstraint(
                check=Q(status__in=[c[0] for c in STATUS_CHOICES]),
                name="valid_invoice_status",
            ),
        ]

    def clean(self):
        # Require payment method for issued invoices
        if self.status == STATUS_ISSUED and not self.payment_method:
            raise ValidationError("Payment method is required when invoice is issued.")

        # Require at least one line item (only if invoice already exists OR being created)
        if self.pk and self.line_items.count() == 0:
            raise ValidationError("Invoice must contain at least one line item.")

    def update_totals(self):
        """Recalculate subtotal, discount, and total_due based on line items."""
        totals = self.line_items.aggregate(
            subtotal=Sum(F("line_subtotal")),
            discount_total=Sum(F("line_discount_total")),
        )
        self.subtotal = totals.get("subtotal") or 0
        self.discount_total = totals.get("discount_total") or 0
        self.total_due = self.subtotal - self.discount_total

    @staticmethod
    def generate_next_invoice_number() -> str:
        """
        Generate the next invoice number in the format EIN00001, EIN00002, ...
        based on the highest existing EIN number.
        """
        last_number = (
            Invoice.objects.filter(invoice_number__startswith="EIN")
            .order_by("-invoice_number")
            .values_list("invoice_number", flat=True)
            .first()
        )

        if not last_number:
            return "EIN00001"

        numeric_part = int(last_number.replace("EIN", ""))
        next_number = numeric_part + 1
        return f"EIN{next_number:05d}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        # Auto-generate number only if missing
        if is_new and not self.invoice_number:
            self.invoice_number = Invoice.generate_next_invoice_number()

        super().save(*args, **kwargs)

        # mark for line-items so they know this is the creation cycle
        self._during_creation = is_new

        # keep totals in sync
        self.update_totals()
        super().save(update_fields=["subtotal", "discount_total", "total_due"])
        
        if self.customer:
            self.customer.update_loyalty_status_from_invoices()

    @property
    def is_locked(self) -> bool:
        """
        Returns True if the invoice status is 'ISSUED', indicating that the invoice
        is locked and cannot be edited. Otherwise, returns False.
        """
        return self.status == STATUS_ISSUED

    def __str__(self):
        return f"Invoice {self.invoice_number}"