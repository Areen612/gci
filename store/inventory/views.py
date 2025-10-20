from __future__ import annotations

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import F, Q
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import InventoryItemForm, StockAdjustmentForm
from .models import InventoryItem, StockAdjustment


class InventoryListView(PermissionRequiredMixin, ListView):
    model = InventoryItem
    template_name = 'inventory/item_list.html'
    context_object_name = 'items'
    paginate_by = 25
    permission_required = 'inventory.view_inventoryitem'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(sku__icontains=query)
                | Q(name__icontains=query)
                | Q(category__icontains=query)
            )
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        stock_filter = self.request.GET.get('stock')
        if stock_filter == 'low':
            queryset = queryset.filter(stock_on_hand__lte=F('reorder_level'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['status'] = self.request.GET.get('status', '')
        context['stock_filter'] = self.request.GET.get('stock', '')
        return context


class InventoryCreateView(PermissionRequiredMixin, CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    permission_required = 'inventory.add_inventoryitem'

    def get_success_url(self):
        messages.success(self.request, 'Inventory item created successfully.')
        return reverse('inventory:item-detail', args=[self.object.pk])


class InventoryDetailView(PermissionRequiredMixin, DetailView):
    model = InventoryItem
    template_name = 'inventory/item_detail.html'
    context_object_name = 'item'
    permission_required = 'inventory.view_inventoryitem'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['adjustments'] = self.object.adjustments.all()
        return context


class InventoryUpdateView(PermissionRequiredMixin, UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    permission_required = 'inventory.change_inventoryitem'

    def get_success_url(self):
        messages.success(self.request, 'Inventory item updated successfully.')
        return reverse('inventory:item-detail', args=[self.object.pk])


class InventoryDeleteView(PermissionRequiredMixin, DeleteView):
    model = InventoryItem
    template_name = 'inventory/item_confirm_delete.html'
    success_url = reverse_lazy('inventory:item-list')
    permission_required = 'inventory.delete_inventoryitem'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Inventory item deleted successfully.')
        return super().delete(request, *args, **kwargs)


class StockAdjustmentCreateView(PermissionRequiredMixin, CreateView):
    model = StockAdjustment
    form_class = StockAdjustmentForm
    template_name = 'inventory/stock_adjustment_form.html'
    permission_required = 'inventory.add_stockadjustment'

    def dispatch(self, request, *args, **kwargs):
        self.item = InventoryItem.objects.get(pk=kwargs['item_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = self.item
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['item'].queryset = InventoryItem.objects.filter(pk=self.item.pk)
        form.fields['item'].initial = self.item
        form.fields['item'].widget = forms.HiddenInput()
        return form

    def form_valid(self, form):
        form.instance.item = self.item
        self.object = form.save(user=self.request.user)
        messages.success(self.request, 'Stock adjustment recorded successfully.')
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('inventory:item-detail', args=[self.item.pk])


class StockAdjustmentHistoryView(PermissionRequiredMixin, ListView):
    model = StockAdjustment
    template_name = 'inventory/stock_adjustment_history.html'
    context_object_name = 'adjustments'
    permission_required = 'inventory.view_stockadjustment'

    def dispatch(self, request, *args, **kwargs):
        self.item = InventoryItem.objects.get(pk=kwargs['item_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.item.adjustments.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = self.item
        return context
