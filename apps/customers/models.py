from __future__ import annotations

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Customer(models.Model):
    """Represents a store customer and their loyalty profile."""

    class LoyaltyStatus(models.TextChoices):
        NONE = "None", "None"
        SILVER = "Silver", "Silver"
        GOLD = "Gold", "Gold"
        PLATINUM = "Platinum", "Platinum"

    class ContactMethod(models.TextChoices):
        EMAIL = "Email", "Email"
        SMS = "SMS", "SMS"
        PHONE = "Phone", "Phone"
        NONE = "None", "None"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    loyalty_status = models.CharField(
        max_length=10,
        choices=LoyaltyStatus.choices,
        default=LoyaltyStatus.NONE,
    )
    date_of_birth = models.DateField(null=True, blank=True)
    preferred_contact_method = models.CharField(
        max_length=10,
        choices=ContactMethod.choices,
        default=ContactMethod.NONE,
    )
    billing_address = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["first_name", "last_name", "email"],
                condition=Q(email__isnull=False),
                name="uniq_customer_name_email",
            ),
            models.UniqueConstraint(
                fields=["first_name", "last_name", "phone_number"],
                condition=Q(phone_number__isnull=False),
                name="uniq_customer_name_phone",
            ),
            models.CheckConstraint(
                check=Q(preferred_contact_method=ContactMethod.NONE)
                | Q(email__isnull=False)
                | Q(phone_number__isnull=False),
                name="preferred_contact_requires_contact",
            ),
        ]

    def clean(self) -> None:  # type: ignore[override]
        if self.preferred_contact_method == self.ContactMethod.EMAIL and not self.email:
            raise ValidationError("Email is required when preferred contact method is Email.")
        if self.preferred_contact_method == self.ContactMethod.SMS and not self.phone_number:
            raise ValidationError("Phone number is required when preferred contact method is SMS.")
        if self.preferred_contact_method == self.ContactMethod.PHONE and not self.phone_number:
            raise ValidationError("Phone number is required when preferred contact method is Phone.")

    def save(self, *args, **kwargs):  # type: ignore[override]
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
