from django.db import models
from .invoice import Invoice
from .discount import Discount

class InvoiceDiscount(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("invoice", "discount")

    def __str__(self):
        return f"{self.discount.name} applied to {self.invoice.invoice_number}"