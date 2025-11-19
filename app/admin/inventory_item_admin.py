from __future__ import annotations

from django.contrib import admin

from app.models import InventoryItem


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "category", "stock_on_hand", "stock_reserved", "is_active")
    search_fields = ("sku", "name", "category")
    list_filter = ("category", "is_active")
