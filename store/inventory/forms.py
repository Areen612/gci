from __future__ import annotations

from django import forms

from .models import InventoryItem, StockAdjustment


class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = [
            'sku',
            'name',
            'category',
            'description',
            'reorder_level',
            'reorder_quantity',
            'unit_cost',
            'unit_price',
            'stock_on_hand',
            'is_active',
        ]

    def clean(self):
        cleaned = super().clean()
        unit_cost = cleaned.get('unit_cost')
        unit_price = cleaned.get('unit_price')
        if unit_cost is not None and unit_price is not None and unit_price < unit_cost:
            self.add_error('unit_price', 'Unit price must be greater than or equal to the unit cost.')
        return cleaned


class StockAdjustmentForm(forms.ModelForm):
    class Meta:
        model = StockAdjustment
        fields = ['item', 'quantity_change', 'reason', 'note']

    def save(self, user=None, commit=True):
        adjustment = super().save(commit=False)
        if user and not adjustment.created_by:
            adjustment.created_by = user
        if commit:
            adjustment.save()
        return adjustment
