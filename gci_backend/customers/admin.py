from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone_number", "loyalty_status", "is_active")
    search_fields = ("first_name", "last_name", "email", "phone_number")
    list_filter = ("loyalty_status", "is_active")
