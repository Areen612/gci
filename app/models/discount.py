from django.db import models

class Discount(models.Model):
    PERCENTAGE = "percentage"
    FIXED = "fixed_amount"

    TYPE_CHOICES = [
        (PERCENTAGE, "Percentage"),
        (FIXED, "Fixed amount"),
    ]

    id = models.UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    applies_to_shipping = models.BooleanField(default=False)

    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name