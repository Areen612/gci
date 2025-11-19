from __future__ import annotations

from django.contrib import admin

from app.models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone_number", "loyalty_status")
    search_fields = ("first_name", "last_name", "email", "phone_number")
    list_filter = ("loyalty_status", "preferred_contact_method")