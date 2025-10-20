from __future__ import annotations

from django import forms

from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "loyalty_status",
            "date_of_birth",
            "preferred_contact_method",
            "is_active",
        ]

    def clean(self):
        cleaned_data = super().clean()
        preferred_method = cleaned_data.get("preferred_contact_method")
        email = cleaned_data.get("email")
        phone_number = cleaned_data.get("phone_number")
        errors: dict[str, str] = {}

        if preferred_method == Customer.ContactMethod.EMAIL and not email:
            errors["email"] = "Email is required when email is the preferred contact method."
        if preferred_method in {
            Customer.ContactMethod.SMS,
            Customer.ContactMethod.PHONE,
        } and not phone_number:
            errors["phone_number"] = "Phone number is required when phone/SMS is preferred."

        if errors:
            raise forms.ValidationError(errors)
        return cleaned_data
