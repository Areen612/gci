from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import migrations, models


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
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("issued", "Issued"),
                            ("paid", "Paid"),
                            ("cancelled", "Cancelled"),
                            ("refunded", "Refunded"),
                        ],
                        default="draft",
                        max_length=12,
                    ),
                ),
                ("invoice_number", models.CharField(max_length=32, unique=True)),
                ("invoice_date", models.DateField()),
                ("due_date", models.DateField(blank=True, null=True)),
                (
                    "subtotal_amount",
                    models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=10),
                ),
                (
                    "tax_amount",
                    models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=10),
                ),
                (
                    "discount_amount",
                    models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=10),
                ),
                (
                    "total_amount",
                    models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=10),
                ),
                (
                    "payment_method",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("cash", "Cash"),
                            ("card", "Card"),
                            ("mobile", "Mobile"),
                            ("gift_card", "Gift card"),
                            ("account", "On account"),
                        ],
                        max_length=20,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=models.deletion.PROTECT,
                        related_name="invoices",
                        to="customers.customer",
                    ),
                ),
            ],
            options={
                "ordering": ["-invoice_date", "invoice_number"],
            },
        ),
        migrations.CreateModel(
            name="InvoiceLine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "quantity",
                    models.PositiveIntegerField(validators=[MinValueValidator(1)]),
                ),
                (
                    "unit_price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[MinValueValidator(Decimal("0"))],
                    ),
                ),
                (
                    "tax_rate",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=5,
                        validators=[MinValueValidator(Decimal("0"))],
                    ),
                ),
                (
                    "discount_amount",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0"),
                        max_digits=10,
                        validators=[MinValueValidator(Decimal("0"))],
                    ),
                ),
                ("description", models.CharField(max_length=100)),
                (
                    "line_subtotal",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0"),
                        editable=False,
                        max_digits=10,
                    ),
                ),
                (
                    "tax_amount",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0"),
                        editable=False,
                        max_digits=10,
                    ),
                ),
                (
                    "invoice",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="lines",
                        to="invoices.invoice",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="invoice_lines",
                        to="inventory.product",
                    ),
                ),
            ],
            options={"ordering": ["pk"]},
        ),
    ]
