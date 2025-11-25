from __future__ import annotations
from django.contrib import admin
from app.models import Seller

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "tax_number")