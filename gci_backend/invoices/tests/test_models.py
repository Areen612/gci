from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from gci_backend.customers.models import Customer
from gci_backend.inventory.models import Product
from gci_backend.invoices.models import Invoice, InvoiceLine


@pytest.fixture
def customer():
    return Customer.objects.create(
        first_name="Invoice",
        last_name="Owner",
        preferred_contact_method=Customer.ContactMethod.NONE,
    )


@pytest.fixture
def product():
    return Product.objects.create(
        sku="SKU-1",
        name="Consulting",
        category="Services",
        unit_price=Decimal("50.00"),
    )


@pytest.mark.django_db
def test_invoice_due_date_validation(customer):
    invoice = Invoice(
        customer=customer,
        invoice_number="INV-1",
        status=Invoice.Status.DRAFT,
        invoice_date=date.today(),
        due_date=date.today() - timedelta(days=1),
        subtotal_amount=Decimal("0"),
        tax_amount=Decimal("0"),
        discount_amount=Decimal("0"),
        total_amount=Decimal("0"),
    )
    with pytest.raises(ValidationError) as exc:
        invoice.full_clean()
    assert "due_date" in exc.value.message_dict


@pytest.mark.django_db
def test_invoice_status_transition_rules(customer):
    invoice = Invoice.objects.create(
        customer=customer,
        invoice_number="INV-100",
        status=Invoice.Status.DRAFT,
        invoice_date=date.today(),
        subtotal_amount=Decimal("0"),
        tax_amount=Decimal("0"),
        discount_amount=Decimal("0"),
        total_amount=Decimal("0"),
    )
    invoice.status = Invoice.Status.PAID
    invoice.total_amount = Decimal("10.00")
    with pytest.raises(ValidationError) as exc:
        invoice.full_clean()
    assert "status" in exc.value.message_dict


@pytest.mark.django_db
def test_invoice_paid_requires_payment_method(customer):
    invoice = Invoice(
        customer=customer,
        invoice_number="INV-200",
        status=Invoice.Status.PAID,
        invoice_date=date.today(),
        subtotal_amount=Decimal("10.00"),
        tax_amount=Decimal("0"),
        discount_amount=Decimal("0"),
        total_amount=Decimal("10.00"),
    )
    with pytest.raises(ValidationError) as exc:
        invoice.full_clean()
    assert "payment_method" in exc.value.message_dict


@pytest.mark.django_db
def test_invoice_line_discount_validation(customer, product):
    invoice = Invoice.objects.create(
        customer=customer,
        invoice_number="INV-300",
        status=Invoice.Status.DRAFT,
        invoice_date=date.today(),
        subtotal_amount=Decimal("0"),
        tax_amount=Decimal("0"),
        discount_amount=Decimal("0"),
        total_amount=Decimal("0"),
    )
    line = InvoiceLine(
        invoice=invoice,
        product=product,
        description="Consulting",
        quantity=1,
        unit_price=Decimal("50.00"),
        tax_rate=Decimal("10.00"),
        discount_amount=Decimal("60.00"),
    )
    with pytest.raises(ValidationError) as exc:
        line.full_clean()
    assert "discount_amount" in exc.value.message_dict


@pytest.mark.django_db
def test_invoice_totals_recalculated_on_line_save(customer, product):
    invoice = Invoice.objects.create(
        customer=customer,
        invoice_number="INV-400",
        status=Invoice.Status.DRAFT,
        invoice_date=date.today(),
        subtotal_amount=Decimal("0"),
        tax_amount=Decimal("0"),
        discount_amount=Decimal("0"),
        total_amount=Decimal("0"),
    )
    InvoiceLine.objects.create(
        invoice=invoice,
        product=product,
        description="Consulting",
        quantity=2,
        unit_price=Decimal("100.00"),
        tax_rate=Decimal("5.00"),
        discount_amount=Decimal("10.00"),
    )
    invoice.refresh_from_db()
    assert invoice.subtotal_amount == Decimal("200.00")
    assert invoice.discount_amount == Decimal("10.00")
    assert invoice.tax_amount == Decimal("9.50")
    assert invoice.total_amount == Decimal("199.50")

    line = invoice.lines.first()
    line.quantity = 3
    line.save()
    invoice.refresh_from_db()
    assert invoice.subtotal_amount == Decimal("300.00")
    assert invoice.discount_amount == Decimal("10.00")
    assert invoice.tax_amount == Decimal("14.50")
    assert invoice.total_amount == Decimal("304.50")
