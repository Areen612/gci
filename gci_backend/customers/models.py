from __future__ import annotations

from datetime import date

from django.core.exceptions import ValidationError
from django.db import models

from gci_backend.core.models import TimeStampedModel


class Customer(TimeStampedModel):
    class LoyaltyStatus(models.TextChoices):
        NONE = "none", "None"
        SILVER = "silver", "Silver"
        GOLD = "gold", "Gold"
        PLATINUM = "platinum", "Platinum"

    class ContactMethod(models.TextChoices):
        NONE = "none", "None"
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        PHONE = "phone", "Phone"

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    loyalty_status = models.CharField(
        max_length=12, choices=LoyaltyStatus.choices, default=LoyaltyStatus.NONE
    )
    date_of_birth = models.DateField(null=True, blank=True)
    preferred_contact_method = models.CharField(
        max_length=10, choices=ContactMethod.choices, default=ContactMethod.NONE
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["first_name", "last_name", "email", "phone_number"],
                name="customer_identity_unique",
            )
        ]
        ordering = ["last_name", "first_name"]

    def clean(self) -> None:
        errors: dict[str, str] = {}
        if self.preferred_contact_method == self.ContactMethod.EMAIL and not self.email:
            errors["email"] = "Email is required when preferred contact method is email."
        if self.preferred_contact_method == self.ContactMethod.SMS and not self.phone_number:
            errors["phone_number"] = "Phone number required for SMS contact preference."
        if self.preferred_contact_method == self.ContactMethod.PHONE and not self.phone_number:
            errors["phone_number"] = "Phone number required for phone contact preference."
        if self.date_of_birth and self.date_of_birth > date.today():
            errors["date_of_birth"] = "Date of birth must be in the past."
        if errors:
            raise ValidationError(errors)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self) -> str:
        return self.full_name
