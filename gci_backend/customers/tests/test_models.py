from __future__ import annotations

from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError

from gci_backend.customers.models import Customer


@pytest.mark.django_db
def test_preferred_contact_requires_email():
    customer = Customer(
        first_name="Jane",
        last_name="Doe",
        preferred_contact_method=Customer.ContactMethod.EMAIL,
    )
    with pytest.raises(ValidationError) as exc:
        customer.full_clean()
    assert "email" in exc.value.message_dict


@pytest.mark.django_db
def test_preferred_contact_requires_phone():
    customer = Customer(
        first_name="John",
        last_name="Smith",
        preferred_contact_method=Customer.ContactMethod.SMS,
    )
    with pytest.raises(ValidationError) as exc:
        customer.full_clean()
    assert "phone_number" in exc.value.message_dict


@pytest.mark.django_db
def test_date_of_birth_must_be_past():
    customer = Customer(
        first_name="Future",
        last_name="Person",
        preferred_contact_method=Customer.ContactMethod.NONE,
        date_of_birth=date.today() + timedelta(days=1),
    )
    with pytest.raises(ValidationError) as exc:
        customer.full_clean()
    assert "date_of_birth" in exc.value.message_dict


@pytest.mark.django_db
def test_unique_identity_constraint():
    Customer.objects.create(
        first_name="Alex",
        last_name="Jones",
        email="alex@example.com",
        phone_number="+15555550000",
        preferred_contact_method=Customer.ContactMethod.EMAIL,
    )
    duplicate = Customer(
        first_name="Alex",
        last_name="Jones",
        email="alex@example.com",
        phone_number="+15555550000",
        preferred_contact_method=Customer.ContactMethod.EMAIL,
    )
    with pytest.raises(ValidationError):
        duplicate.validate_unique()
