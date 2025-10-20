from __future__ import annotations

import pytest
from django.urls import reverse

from gci_backend.customers.models import Customer


@pytest.mark.django_db
def test_customer_create_view_success(client):
    response = client.post(
        reverse("customers:create"),
        data={
            "first_name": "Jamie",
            "last_name": "Rivera",
            "preferred_contact_method": Customer.ContactMethod.NONE,
            "is_active": "on",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert Customer.objects.filter(first_name="Jamie").exists()


@pytest.mark.django_db
def test_customer_create_view_validation_error(client):
    response = client.post(
        reverse("customers:create"),
        data={
            "first_name": "Taylor",
            "last_name": "Nguyen",
            "preferred_contact_method": Customer.ContactMethod.EMAIL,
        },
    )
    assert response.status_code == 200
    assert "Email is required" in response.content.decode()
    assert not Customer.objects.filter(first_name="Taylor").exists()
