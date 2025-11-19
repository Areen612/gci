from django.db import models
from .invoice import Invoice
from .item import Item

class InvoiceItem(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="line_items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    total_after_discount = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)

    line_subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    line_tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.item.name} × {self.quantity}"