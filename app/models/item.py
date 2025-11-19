from django.db import models

class Item(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    sku = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    taxable = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name