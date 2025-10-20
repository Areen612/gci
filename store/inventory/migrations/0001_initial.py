# Generated manually for initial schema
from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku', models.CharField(max_length=32, unique=True)),
                ('name', models.CharField(max_length=120)),
                ('category', models.CharField(max_length=80)),
                ('description', models.TextField(blank=True)),
                ('reorder_level', models.PositiveIntegerField(default=0)),
                ('reorder_quantity', models.PositiveIntegerField(default=0)),
                ('unit_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('stock_on_hand', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='StockAdjustment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'quantity_change',
                    models.IntegerField(help_text='Positive to add stock, negative to remove.'),
                ),
                ('reason', models.CharField(max_length=255)),
                ('note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resulting_quantity', models.PositiveIntegerField(editable=False)),
                (
                    'created_by',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='stock_adjustments',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'item',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='adjustments',
                        to='inventory.inventoryitem',
                    ),
                ),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
