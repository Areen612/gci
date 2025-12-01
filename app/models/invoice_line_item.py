import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from .invoice import Invoice
from .item import Item

class InvoiceLineItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Many-to-One (ForeignKey): Multiple InvoiceLineItems belong to one Invoice
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="line_items") 
    # Many-to-One (ForeignKey): Each line item references one Item
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)
    item_name = models.CharField(max_length=255, default="Unknown Item")
    
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=3)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=3, default=0)

    line_subtotal = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    line_discount_total = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    total_after_discount = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(quantity__gt=0), name="line_quantity_positive"),
            models.CheckConstraint(check=Q(unit_price__gte=0), name="line_unit_price_non_negative"),
            models.CheckConstraint(check=Q(line_subtotal__gte=0), name="line_subtotal_non_negative"),
            models.CheckConstraint(check=Q(discount_amount__gte=0), name="line_discount_non_negative"),
            models.CheckConstraint(
                check=Q(discount_amount__lte=F("line_subtotal")),
                name="line_discount_lte_subtotal",
            ),
        ]

    def clean(self):
        self.calculate_totals()

        # skip locking completely during invoice creation
        if hasattr(self.invoice, "_during_creation") and self.invoice._during_creation:
            return

        # enforce locking only on existing invoices
        if self.invoice and self.invoice.pk and self.invoice.is_locked:
            raise ValidationError("Issued invoices cannot be modified.")

        if self.discount_amount > self.line_subtotal:
            raise ValidationError("Discount amount cannot exceed the line subtotal.")

    def calculate_totals(self):
        self.line_subtotal = self.quantity * self.unit_price
        self.line_discount_total = self.discount_amount
        self.total_after_discount = self.line_subtotal - self.line_discount_total
        
    def save(self, *args, **kwargs):
        is_new = self.pk is None

        super().save(*args, **kwargs)

        # Mark invoice state so line items know this is the first save cycle
        self._during_creation = is_new

        # Update totals after creation
        self.invoice.update_totals()
        self.invoice.save(update_fields=["subtotal", "discount_total", "total_due"])
    
    def __str__(self):
        return self.item_name