from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from django.urls import reverse

from gci_backend.customers.models import Customer
from gci_backend.inventory.models import Product
from gci_backend.invoices.models import Invoice


@pytest.fixture
def customer():
    return Customer.objects.create(
        first_name="Casey",
        last_name="Lee",
        preferred_contact_method=Customer.ContactMethod.NONE,
    )


@pytest.fixture
def product():
    return Product.objects.create(
        sku="SKU-10",
        name="Service",
        category="Services",
        unit_price=Decimal("40.00"),
    )


@pytest.mark.django_db
def test_invoice_create_view_success(client, customer, product):
    response = client.post(
        reverse("invoices:create"),
        data={
            "customer": customer.pk,
            "invoice_number": "INV-900",
            "status": Invoice.Status.DRAFT,
            "invoice_date": date.today(),
            "due_date": date.today(),
            "payment_method": "",
            "notes": "",
            "invoiceline_set-TOTAL_FORMS": "1",
            "invoiceline_set-INITIAL_FORMS": "0",
            "invoiceline_set-MIN_NUM_FORMS": "0",
            "invoiceline_set-MAX_NUM_FORMS": "1000",
            "invoiceline_set-0-product": product.pk,
            "invoiceline_set-0-description": "Service",
            "invoiceline_set-0-quantity": "2",
            "invoiceline_set-0-unit_price": "40.00",
            "invoiceline_set-0-tax_rate": "10.00",
            "invoiceline_set-0-discount_amount": "5.00",
        },
        follow=True,
    )
    assert response.status_code == 200
    invoice = Invoice.objects.get(invoice_number="INV-900")
    assert invoice.subtotal_amount == Decimal("80.00")
    assert invoice.discount_amount == Decimal("5.00")
    assert invoice.tax_amount == Decimal("7.50")
    assert invoice.total_amount == Decimal("82.50")


@pytest.mark.django_db
def test_invoice_create_view_validation_error(client, customer, product):
    response = client.post(
        reverse("invoices:create"),
        data={
            "customer": customer.pk,
            "invoice_number": "INV-901",
            "status": Invoice.Status.DRAFT,
            "invoice_date": date.today(),
            "due_date": date.today() - date.resolution,
            "payment_method": "",
            "notes": "",
            "invoiceline_set-TOTAL_FORMS": "1",
            "invoiceline_set-INITIAL_FORMS": "0",
            "invoiceline_set-MIN_NUM_FORMS": "0",
            "invoiceline_set-MAX_NUM_FORMS": "1000",
            "invoiceline_set-0-product": product.pk,
            "invoiceline_set-0-description": "Service",
            "invoiceline_set-0-quantity": "1",
            "invoiceline_set-0-unit_price": "40.00",
            "invoiceline_set-0-tax_rate": "10.00",
            "invoiceline_set-0-discount_amount": "0",
        },
    )
    assert response.status_code == 200
    assert "Due date cannot" in response.content.decode()
    assert not Invoice.objects.filter(invoice_number="INV-901").exists()
