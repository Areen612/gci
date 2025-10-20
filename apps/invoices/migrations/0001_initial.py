# Generated manually to bootstrap the invoices app.
from __future__ import annotations

import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("customers", "0001_initial"),
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("invoice_number", models.CharField(max_length=50, unique=True)),
                ("invoice_date", models.DateTimeField()),
                ("due_date", models.DateField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Draft", "Draft"),
                            ("Issued", "Issued"),
                            ("Paid", "Paid"),
                            ("Cancelled", "Cancelled"),
                            ("Refunded", "Refunded"),
                        ],
                        default="Draft",
                        max_length=10,
                    ),
                ),
                ("subtotal_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("tax_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("discount_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "payment_method",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Cash", "Cash"),
                            ("Card", "Card"),
                            ("Mobile", "Mobile"),
                            ("GiftCard", "Gift Card"),
                            ("Account", "Account"),
                        ],
                        max_length=10,
                    ),
                ),
                ("notes", models.TextField(blank=True, max_length=500)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="invoices",
                        to="customers.customer",
                    ),
                ),
            ],
            options={"ordering": ["-invoice_date"]},
        ),
        migrations.CreateModel(
            name="InvoiceLineItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("description", models.CharField(max_length=100)),
                ("quantity", models.PositiveIntegerField()),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("line_subtotal", models.DecimalField(decimal_places=2, max_digits=10)),
                ("tax_rate", models.DecimalField(decimal_places=2, max_digits=5)),
                ("tax_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("discount_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "inventory_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="line_items",
                        to="inventory.inventoryitem",
                    ),
                ),
                (
                    "invoice",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="line_items",
                        to="invoices.invoice",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="invoice",
            constraint=models.CheckConstraint(check=models.Q(subtotal_amount__gte=0), name="subtotal_non_negative"),
        ),
        migrations.AddConstraint(
            model_name="invoice",
            constraint=models.CheckConstraint(check=models.Q(tax_amount__gte=0), name="tax_non_negative"),
        ),
        migrations.AddConstraint(
            model_name="invoice",
            constraint=models.CheckConstraint(check=models.Q(discount_amount__gte=0), name="discount_non_negative"),
        ),
        migrations.AddConstraint(
            model_name="invoice",
            constraint=models.CheckConstraint(
                check=models.Q(discount_amount__lte=models.F("subtotal_amount")),
                name="discount_lte_subtotal",
            ),
        ),
        migrations.AddConstraint(
            model_name="invoice",
            constraint=models.CheckConstraint(check=models.Q(total_amount__gte=0), name="total_non_negative"),
        ),
        migrations.AddConstraint(
            model_name="invoice",
            constraint=models.CheckConstraint(
                check=models.Q(status__in=["Draft", "Issued", "Paid", "Cancelled", "Refunded"]),
                name="valid_invoice_status",
            ),
        ),
        migrations.AddConstraint(
            model_name="invoicelineitem",
            constraint=models.CheckConstraint(check=models.Q(quantity__gt=0), name="line_quantity_positive"),
        ),
        migrations.AddConstraint(
            model_name="invoicelineitem",
            constraint=models.CheckConstraint(check=models.Q(unit_price__gte=0), name="line_unit_price_non_negative"),
        ),
        migrations.AddConstraint(
            model_name="invoicelineitem",
            constraint=models.CheckConstraint(check=models.Q(line_subtotal__gte=0), name="line_subtotal_non_negative"),
        ),
        migrations.AddConstraint(
            model_name="invoicelineitem",
            constraint=models.CheckConstraint(check=models.Q(tax_amount__gte=0), name="line_tax_non_negative"),
        ),
        migrations.AddConstraint(
            model_name="invoicelineitem",
            constraint=models.CheckConstraint(check=models.Q(discount_amount__gte=0), name="line_discount_non_negative"),
        ),
        migrations.AddConstraint(
            model_name="invoicelineitem",
            constraint=models.CheckConstraint(
                check=models.Q(discount_amount__lte=models.F("line_subtotal")),
                name="line_discount_lte_subtotal",
            ),
        ),
    ]
