from django.db import models

class Seller(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    mobile = models.CharField(max_length=50, null=True, blank=True)
    tax_number = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.mobile})" if self.mobile else self.name