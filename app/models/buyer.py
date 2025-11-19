from django.db import models

class Buyer(models.Model):
    name = models.CharField(max_length=255)
    additional_id = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name