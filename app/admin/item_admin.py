from django.contrib import admin
from app.models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    search_fields = ("name", "sku")
    list_display = ("name", "sku", "base_price")