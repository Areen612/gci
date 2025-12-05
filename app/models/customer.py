from __future__ import annotations
import uuid
import re
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import models
from django.db.models import Q

from django.utils import timezone


class LoyaltySettings(models.Model):
    """Configurable loyalty thresholds used to auto-assign customer status."""

    silver_threshold = models.PositiveIntegerField(default=50)
    gold_threshold = models.PositiveIntegerField(default=250)
    platinum_threshold = models.PositiveIntegerField(default=500)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Loyalty settings"

    def clean(self) -> None:
        super().clean()

        if not (self.silver_threshold < self.gold_threshold < self.platinum_threshold):
            raise ValidationError(
                "Thresholds must increase from Silver to Gold to Platinum."
            )

    @classmethod
    def get_solo(cls) -> "LoyaltySettings":
        settings, _ = cls.objects.get_or_create(
            defaults={
                "silver_threshold": 50,
                "gold_threshold": 250,
                "platinum_threshold": 500,
                "updated_at": timezone.now(),
            }
        )
        return settings

    def __str__(self) -> str:
        return "Loyalty thresholds"



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
    email = models.EmailField(unique=True, null=True, blank=True, validators=[EmailValidator()])
    phone_number = models.CharField(max_length=10, unique=False, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)  # Customer field
    loyalty_status = models.CharField(
        max_length=10,
        choices=LoyaltyStatus.choices,
        default=LoyaltyStatus.NONE,
    )
    loyalty_status_locked = models.BooleanField(
        default=False,
        help_text=(
            "Lock the loyalty status to prevent automatic changes based on invoice "
            "count."
        ),
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
        
        if self.phone_number and not re.match(r'^\d{10}$', self.phone_number):
            raise ValidationError("Phone number must be exactly 10 digits.")

    def calculate_loyalty_status(
        self,
        invoice_count: int | None = None,
        settings: LoyaltySettings | None = None,
    ) -> str:
        settings = settings or LoyaltySettings.get_solo()
        invoice_total = invoice_count if invoice_count is not None else (self.invoices.count() if self.pk else 0)

        if invoice_total >= settings.platinum_threshold:
            return self.LoyaltyStatus.PLATINUM
        if invoice_total >= settings.gold_threshold:
            return self.LoyaltyStatus.GOLD
        if invoice_total >= settings.silver_threshold:
            return self.LoyaltyStatus.SILVER
        return self.LoyaltyStatus.NONE

    def update_loyalty_status_from_invoices(
        self, *, commit: bool = True, settings: LoyaltySettings | None = None
    ) -> bool:
        if self.loyalty_status_locked:
            return False

        invoice_total = self.invoices.count() if self.pk else 0
        new_status = self.calculate_loyalty_status(
            invoice_count=invoice_total, settings=settings
        )
        if new_status == self.loyalty_status:
            return False

        self.loyalty_status = new_status
        if commit:
            super(Customer, self).save(update_fields=["loyalty_status", "updated_at"])
        return True

    def save(self, *args, **kwargs) -> None:
        if not self.loyalty_status_locked:
            self.loyalty_status = self.calculate_loyalty_status()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name or "Customer"