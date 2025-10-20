from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from gci_backend.core.models import TimeStampedModel


class Product(TimeStampedModel):
    sku = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50)
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))]
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"
