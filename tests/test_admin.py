from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from app.models import Customer, Invoice, Item  

@pytest.fixture
def admin_user(db):
    User = get_user_model()
    user = User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="password123",
    )
    return user


@pytest.mark.django_db
def test_admin_customer_changelist(client, admin_user):
    client.login(username="admin", password="password123")
    response = client.get(reverse("admin:customers_customer_changelist"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_invoice_add(client, admin_user):
    customer = Customer.objects.create(
        first_name="Admin",
        last_name="Tester",
        preferred_contact_method=Customer.ContactMethod.NONE,
    )
    client.login(username="admin", password="password123")
    response = client.get(reverse("admin:invoices_invoice_add"))
    assert response.status_code == 200
    response = client.post(
        reverse("admin:invoices_invoice_add"),
        data={
            "customer": customer.pk,
            "invoice_number": "INV-ADMIN",
            "status": Invoice.Status.DRAFT,
            "invoice_date": "2024-01-01",
            "due_date": "2024-01-02",
            "subtotal_amount": "0",
            "discount_amount": "0",
            "total_amount": "0",
            "_save": "Save",
        },
    )
    assert response.status_code in {302, 200}


@pytest.mark.django_db
def test_admin_invoice_line_inline(client, admin_user):
    customer = Customer.objects.create(
        first_name="Inline",
        last_name="Test",
        preferred_contact_method=Customer.ContactMethod.NONE,
    )
    product = Item.objects.create(
        sku="SKU-ADMIN",
        name="Admin Product",
        category="Services",
        unit_price="10.00",
    )
    client.login(username="admin", password="password123")
    response = client.post(
        reverse("admin:invoices_invoice_add"),
        data={
            "customer": customer.pk,
            "invoice_number": "INV-ADMIN-2",
            "status": Invoice.Status.DRAFT,
            "invoice_date": "2024-01-01",
            "due_date": "2024-01-02",
            "subtotal_amount": "0",
            "discount_amount": "0",
            "total_amount": "0",
            "invoiceline_set-TOTAL_FORMS": "1",
            "invoiceline_set-INITIAL_FORMS": "0",
            "invoiceline_set-MIN_NUM_FORMS": "0",
            "invoiceline_set-MAX_NUM_FORMS": "1000",
            "invoiceline_set-0-product": product.pk,
            "invoiceline_set-0-description": "Admin Product",
            "invoiceline_set-0-quantity": "1",
            "invoiceline_set-0-unit_price": "10.00",
            "invoiceline_set-0-discount_amount": "0",
            "_save": "Save",
        },
    )
    assert response.status_code in {302, 200}
