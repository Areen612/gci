from django.db import models
from django.db.models import Q, F
import uuid
from django.core.exceptions import ValidationError
from .invoice import Invoice
from .item import Item
from app.core.constants import TAX_RATE

class InvoiceLineItem(models.Model):
    """Individual line items that compose an invoice."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="line_items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=3, default=0)

    line_subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_after_discount = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(quantity__gt=0), name="line_quantity_positive"),
            models.CheckConstraint(check=Q(unit_price__gte=0), name="line_unit_price_non_negative"),
            models.CheckConstraint(check=Q(line_subtotal__gte=0), name="line_subtotal_non_negative"),
            models.CheckConstraint(check=Q(line_tax_total__gte=0), name="line_tax_non_negative"),
            models.CheckConstraint(check=Q(discount_amount__gte=0), name="line_discount_non_negative"),
            models.CheckConstraint(
                check=Q(discount_amount__lte=F("line_subtotal")),
                name="line_discount_lte_subtotal",
            ),
        ]

    def clean(self) -> None:
        if self.discount_amount > self.line_subtotal:
            raise ValidationError("Discount amount cannot exceed the line subtotal.")

    def calculate_totals(self):
        self.line_subtotal = self.quantity * self.unit_price
        self.line_discount_total = self.discount_amount

        self.line_tax_total = self.line_subtotal * TAX_RATE

        self.total_after_discount = (
            self.line_subtotal + self.line_tax_total - self.line_discount_total
        )
    def save(self, *args, **kwargs):
        self.calculate_totals()
        super().save(*args, **kwargs)
        # Update parent invoice totals
        self.invoice.update_totals()
        self.invoice.save(update_fields=['subtotal', 'tax_total', 'discount_total', 'total_due'])

    def __str__(self):
        return f"{self.item.name} × {self.quantity}"