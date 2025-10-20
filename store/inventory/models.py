from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction


class InventoryItem(models.Model):
    sku = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    reorder_level = models.PositiveIntegerField(default=0)
    reorder_quantity = models.PositiveIntegerField(default=0)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_on_hand = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"{self.sku} — {self.name}"

    @property
    def is_low_stock(self) -> bool:
        return self.stock_on_hand <= self.reorder_level

    def validate_adjustment(self, quantity_change: int) -> None:
        new_stock = self.stock_on_hand + quantity_change
        if new_stock < 0:
            raise ValidationError(
                {
                    'quantity_change': 'Cannot reduce stock below zero. '
                    f'Current stock: {self.stock_on_hand}.',
                }
            )

    def apply_adjustment(self, quantity_change: int) -> int:
        self.validate_adjustment(quantity_change)
        self.stock_on_hand += quantity_change
        self.save(update_fields=['stock_on_hand', 'updated_at'])
        return self.stock_on_hand


class StockAdjustment(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT, related_name='adjustments')
    quantity_change = models.IntegerField(help_text='Positive to add stock, negative to remove.')
    reason = models.CharField(max_length=255)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='stock_adjustments',
    )
    resulting_quantity = models.PositiveIntegerField(editable=False)

    class Meta:
        ordering = ['-created_at']

    def clean(self) -> None:
        super().clean()
        if self.quantity_change == 0:
            raise ValidationError({'quantity_change': 'Adjustment cannot be zero.'})
        if self.item_id:
            self.item.validate_adjustment(self.quantity_change)

    def save(self, *args, **kwargs):
        is_create = self.pk is None
        with transaction.atomic():
            self.full_clean()
            if is_create:
                new_quantity = self.item.stock_on_hand + self.quantity_change
                self.resulting_quantity = new_quantity
            super().save(*args, **kwargs)
            if is_create:
                self.item.stock_on_hand = self.resulting_quantity
                self.item.save(update_fields=['stock_on_hand', 'updated_at'])
        return self

    def __str__(self) -> str:  # pragma: no cover - simple repr
        direction = 'added' if self.quantity_change > 0 else 'removed'
        return f"{abs(self.quantity_change)} {direction} for {self.item}"
