from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from inventory.models import InventoryItem


class InventoryItemModelTests(TestCase):
    def test_apply_adjustment_updates_stock(self):
        item = InventoryItem.objects.create(
            sku='SKU123',
            name='Test Item',
            category='Category',
            stock_on_hand=5,
        )
        item.apply_adjustment(3)
        item.refresh_from_db()
        self.assertEqual(item.stock_on_hand, 8)

    def test_negative_stock_prevented(self):
        item = InventoryItem.objects.create(
            sku='SKU124',
            name='Another Item',
            category='Category',
            stock_on_hand=2,
        )
        with self.assertRaisesMessage(ValidationError, 'Cannot reduce stock below zero'):
            item.apply_adjustment(-3)


class InventoryViewsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('staff', 'staff@example.com', 'password')
        self.user.is_staff = True
        self.user.save()
        view_perm = Permission.objects.get(codename='view_inventoryitem')
        change_perm = Permission.objects.get(codename='change_inventoryitem')
        add_perm = Permission.objects.get(codename='add_inventoryitem')
        delete_perm = Permission.objects.get(codename='delete_inventoryitem')
        adjust_perm = Permission.objects.get(codename='add_stockadjustment')
        view_adjust_perm = Permission.objects.get(codename='view_stockadjustment')
        self.user.user_permissions.add(
            view_perm,
            change_perm,
            add_perm,
            delete_perm,
            adjust_perm,
            view_adjust_perm,
        )
        self.client.force_login(self.user)

    def test_list_view_search(self):
        InventoryItem.objects.create(sku='ABC123', name='Widget', category='Hardware')
        InventoryItem.objects.create(sku='XYZ987', name='Gadget', category='Electronics')

        response = self.client.get(reverse('inventory:item-list'), {'q': 'Wid'})
        self.assertContains(response, 'Widget')
        self.assertNotContains(response, 'Gadget')

    def test_stock_adjustment_flow(self):
        item = InventoryItem.objects.create(sku='STK1', name='Stock Item', category='General', stock_on_hand=4)
        url = reverse('inventory:adjustment-create', args=[item.pk])
        response = self.client.post(
            url,
            {
                'item': item.pk,
                'quantity_change': 5,
                'reason': 'Received shipment',
                'note': '',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.stock_on_hand, 9)
        adjustment = item.adjustments.first()
        self.assertEqual(adjustment.resulting_quantity, 9)

    def test_negative_adjustment_rejected(self):
        item = InventoryItem.objects.create(sku='NEG', name='Negative Item', category='General', stock_on_hand=1)
        url = reverse('inventory:adjustment-create', args=[item.pk])
        response = self.client.post(
            url,
            {
                'item': item.pk,
                'quantity_change': -5,
                'reason': 'Shrinkage',
                'note': '',
            },
        )
        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.stock_on_hand, 1)
        self.assertFormError(response, 'form', 'quantity_change', 'Cannot reduce stock below zero. Current stock: 1.')
