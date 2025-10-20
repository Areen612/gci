# Generated manually to bootstrap the inventory app.
from __future__ import annotations

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies: list[tuple[str, str]] = []

    operations = [
        migrations.CreateModel(
            name="InventoryItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("sku", models.CharField(max_length=20, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True, max_length=500)),
                ("category", models.CharField(max_length=100)),
                ("reorder_level", models.PositiveIntegerField(default=0)),
                ("reorder_quantity", models.PositiveIntegerField(default=0)),
                ("unit_cost", models.DecimalField(decimal_places=2, max_digits=10)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("stock_on_hand", models.PositiveIntegerField(default=0)),
                ("stock_reserved", models.PositiveIntegerField(default=0)),
                ("supplier_id", models.UUIDField(blank=True, null=True)),
                ("location", models.CharField(blank=True, max_length=50)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["sku"],
                "verbose_name": "Inventory Item",
                "verbose_name_plural": "Inventory Items",
            },
        ),
        migrations.AddConstraint(
            model_name="inventoryitem",
            constraint=models.CheckConstraint(check=models.Q(unit_cost__gte=0), name="unit_cost_non_negative"),
        ),
        migrations.AddConstraint(
            model_name="inventoryitem",
            constraint=models.CheckConstraint(check=models.Q(unit_price__gte=0), name="unit_price_non_negative"),
        ),
        migrations.AddConstraint(
            model_name="inventoryitem",
            constraint=models.CheckConstraint(
                check=models.Q(unit_price__gte=models.F("unit_cost")),
                name="unit_price_above_cost",
            ),
        ),
        migrations.AddConstraint(
            model_name="inventoryitem",
            constraint=models.CheckConstraint(
                check=models.Q(stock_reserved__lte=models.F("stock_on_hand")),
                name="reserved_not_exceed_on_hand",
            ),
        ),
    ]
