# Generated manually to bootstrap the customers app.
from __future__ import annotations

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies: list[tuple[str, str]] = []

    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(max_length=50)),
                ("email", models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ("phone_number", models.CharField(blank=True, max_length=15, null=True, unique=True)),
                (
                    "loyalty_status",
                    models.CharField(
                        choices=[
                            ("None", "None"),
                            ("Silver", "Silver"),
                            ("Gold", "Gold"),
                            ("Platinum", "Platinum"),
                        ],
                        default="None",
                        max_length=10,
                    ),
                ),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                (
                    "preferred_contact_method",
                    models.CharField(
                        choices=[
                            ("Email", "Email"),
                            ("SMS", "SMS"),
                            ("Phone", "Phone"),
                            ("None", "None"),
                        ],
                        default="None",
                        max_length=10,
                    ),
                ),
                ("billing_address", models.JSONField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["last_name", "first_name"]},
        ),
        migrations.AddConstraint(
            model_name="customer",
            constraint=models.UniqueConstraint(
                condition=models.Q(("email__isnull", False)),
                fields=("first_name", "last_name", "email"),
                name="uniq_customer_name_email",
            ),
        ),
        migrations.AddConstraint(
            model_name="customer",
            constraint=models.UniqueConstraint(
                condition=models.Q(("phone_number__isnull", False)),
                fields=("first_name", "last_name", "phone_number"),
                name="uniq_customer_name_phone",
            ),
        ),
        migrations.AddConstraint(
            model_name="customer",
            constraint=models.CheckConstraint(
                check=models.Q(("preferred_contact_method", "None"))
                | models.Q(("email__isnull", False))
                | models.Q(("phone_number__isnull", False)),
                name="preferred_contact_requires_contact",
            ),
        ),
    ]
