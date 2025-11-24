from django.db import models
from .invoice import Invoice
from .tax import Tax

class InvoiceTax(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['invoice', 'tax'], name='unique_invoice_tax')
        ]

    def __str__(self):
        return f"{self.tax.name} on {self.invoice.invoice_number}"