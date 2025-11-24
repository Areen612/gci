from __future__ import annotations
from django.db import models
import uuid
from django.db.models import Q, F

class Item(models.Model):
    """Represents an item tracked in inventory and available for invoicing."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sku = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=500, null=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=3)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)

    stock_on_hand = models.PositiveIntegerField(default=0)
    stock_reserved = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=0)
    reorder_quantity = models.PositiveIntegerField(default=0)
    supplier_id = models.UUIDField(null=True, blank=True)
    location = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sku"]
        verbose_name = "Item"
        verbose_name_plural = "Items"
        constraints = [
            models.CheckConstraint(check=Q(base_price__gte=0), name="base_price_non_negative"),
            models.CheckConstraint(check=Q(unit_cost__gte=0), name="unit_cost_non_negative"),
            models.CheckConstraint(
                check=Q(base_price__gte=F("unit_cost")),
                name="base_price_above_cost"
            ),
            models.CheckConstraint(
                check=Q(stock_reserved__lte=F("stock_on_hand")),
                name="reserved_not_exceed_on_hand"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.sku} - {self.name}"