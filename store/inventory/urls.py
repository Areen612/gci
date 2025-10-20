from __future__ import annotations

from django.urls import path

from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.InventoryListView.as_view(), name='item-list'),
    path('create/', views.InventoryCreateView.as_view(), name='item-create'),
    path('<int:pk>/', views.InventoryDetailView.as_view(), name='item-detail'),
    path('<int:pk>/edit/', views.InventoryUpdateView.as_view(), name='item-update'),
    path('<int:pk>/delete/', views.InventoryDeleteView.as_view(), name='item-delete'),
    path('<int:item_pk>/adjustments/new/', views.StockAdjustmentCreateView.as_view(), name='adjustment-create'),
    path('<int:item_pk>/adjustments/', views.StockAdjustmentHistoryView.as_view(), name='adjustment-history'),
]
