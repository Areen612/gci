from __future__ import annotations
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django import forms
from app.models import Customer
from django.contrib.admin.widgets import AutocompleteSelect

#TODO: Implement advanced search form for Customer admin
class CustomerSearchForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "email", "phone_number"]
        widgets = {
            "name": AutocompleteSelect(
                Customer._meta.get_field("name").remote_field,
                admin.site,
            ),
        }


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    search_fields = ("name__istartswith", "email__istartswith", "phone_number__istartswith")
    list_display = ("name", "email", "phone_number", "invoice_count", "view_invoices")
    list_per_page = 20

    # IMPORTANT: enables autocomplete suggestions
    autocomplete_fields = ["seller"] if hasattr(Customer, "seller") else []

    def get_search_results(self, request, queryset, search_term):
        """
        Enhance search: support suggestions for partial matches.
        """
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if search_term:
            queryset |= self.model.objects.filter(name__icontains=search_term)
            queryset |= self.model.objects.filter(email__icontains=search_term)
            queryset |= self.model.objects.filter(phone_number__icontains=search_term)

        return queryset, use_distinct

    def invoice_count(self, obj):
        return obj.invoices.count()

    def view_invoices(self, obj):
        url = reverse("admin:app_invoice_changelist") + f"?customer__id__exact={obj.id}"
        return format_html(f"<a href='{url}'>View invoices</a>")

    invoice_count.short_description = "Invoices"