from __future__ import annotations

from django.contrib import admin
from django.db.models import F

from .models import InventoryItem, StockAdjustment


class LowStockFilter(admin.SimpleListFilter):
    title = 'Low stock'
    parameter_name = 'low_stock'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Below reorder level'),
            ('no', 'Healthy stock'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(stock_on_hand__lte=F('reorder_level'))
        if self.value() == 'no':
            return queryset.filter(stock_on_hand__gt=F('reorder_level'))
        return queryset


class StockAdjustmentInline(admin.TabularInline):
    model = StockAdjustment
    extra = 0
    readonly_fields = ('quantity_change', 'reason', 'note', 'created_at', 'created_by', 'resulting_quantity')
    can_delete = False


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'name',
        'category',
        'stock_on_hand',
        'reorder_level',
        'is_active',
        'is_low_stock',
    )
    list_filter = ('category', 'is_active', LowStockFilter)
    search_fields = ('sku', 'name', 'category')
    inlines = [StockAdjustmentInline]
    actions = ['mark_active', 'mark_inactive']

    @admin.action(description='Mark selected items as active')
    def mark_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Mark selected items as inactive')
    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('item', 'quantity_change', 'resulting_quantity', 'reason', 'created_at', 'created_by')
    list_filter = ('created_at', 'item__category')
    search_fields = ('item__sku', 'item__name', 'reason', 'note')
    autocomplete_fields = ('item',)
    readonly_fields = ('resulting_quantity',)
