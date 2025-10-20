from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies: list[tuple[str, str]] = []

    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(max_length=50)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("phone_number", models.CharField(blank=True, max_length=20)),
                (
                    "loyalty_status",
                    models.CharField(
                        choices=[
                            ("none", "None"),
                            ("silver", "Silver"),
                            ("gold", "Gold"),
                            ("platinum", "Platinum"),
                        ],
                        default="none",
                        max_length=12,
                    ),
                ),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                (
                    "preferred_contact_method",
                    models.CharField(
                        choices=[
                            ("none", "None"),
                            ("email", "Email"),
                            ("sms", "SMS"),
                            ("phone", "Phone"),
                        ],
                        default="none",
                        max_length=10,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["last_name", "first_name"],
            },
        ),
        migrations.AddConstraint(
            model_name="customer",
            constraint=models.UniqueConstraint(
                fields=("first_name", "last_name", "email", "phone_number"),
                name="customer_identity_unique",
            ),
        ),
    ]
