from django.urls import path
from .views.invoice_views import InvoiceListView

urlpatterns = [
    path("invoices/", InvoiceListView.as_view(), name="invoice-list"),
]