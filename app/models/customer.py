from __future__ import annotations
import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Customer(models.Model):
    """Represents a store customer with detailed profile and contact info."""

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
    name = models.CharField(max_length=255, blank=False)
    
    additional_id = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=50, unique=False, null=True, blank=True)  # Increased max length
    address = models.CharField(max_length=255, null=True, blank=True)  # Customer field
    postal_code = models.CharField(max_length=20, null=True, blank=True)  # Customer field
    loyalty_status = models.CharField(
        max_length=10,
        choices=LoyaltyStatus.choices,
        default=LoyaltyStatus.NONE,
    )
    preferred_contact_method = models.CharField(
        max_length=10,
        choices=ContactMethod.choices,
        default=ContactMethod.NONE,
    )
    billing_address = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "email"],
                condition=Q(email__isnull=False),
                name="uniq_customer_name_email",
            ),
            models.UniqueConstraint(
                fields=["name", "phone_number"],
                condition=Q(phone_number__isnull=False),
                name="uniq_customer_name_phone",
            ),
            models.CheckConstraint(
                check=Q(preferred_contact_method="None")
                | Q(email__isnull=False)
                | Q(phone_number__isnull=False),
                name="preferred_contact_requires_contact",
            ),
        ]

    def clean(self) -> None:
        if self.preferred_contact_method == self.ContactMethod.EMAIL and not self.email:
            raise ValidationError("Email is required when preferred contact method is Email.")
        if self.preferred_contact_method in (self.ContactMethod.SMS, self.ContactMethod.PHONE) and not self.phone_number:
            raise ValidationError("Phone number is required when preferred contact method is SMS or Phone.")
        if not self.name:
            raise ValidationError("Customer name must be provided.")

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        if self.name:
            return self.name
        return f"{self.name}"