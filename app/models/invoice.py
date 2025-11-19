from django.db import models
from .buyer import Buyer
from .seller import Seller

class Invoice(models.Model):
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

    uuid = models.UUIDField(unique=True)
    invoice_number = models.CharField(max_length=100)

    customer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True)
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True)

    invoice_date = models.DateField()
    due_date = models.DateField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # From JOFotara API
    xml = models.TextField(null=True, blank=True)
    qr_base64 = models.TextField(null=True, blank=True)
    qr_image = models.ImageField(upload_to='invoices/qr/', null=True, blank=True)
    e_invoice_number = models.CharField(max_length=50, null=True, blank=True)
    invoice_type = models.CharField(max_length=50, null=True, blank=True)
    sequence_income_number = models.CharField(max_length=50, null=True, blank=True)

    currency_name = models.CharField(max_length=50, null=True, blank=True)

    total_before_discount = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    discount_value = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)

    payment_method = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.invoice_number