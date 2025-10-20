from django.urls import path

from .views import InvoiceCreateView, InvoiceDetailView

app_name = "invoices"

urlpatterns = [
    path("create/", InvoiceCreateView.as_view(), name="create"),
    path("<int:pk>/", InvoiceDetailView.as_view(), name="detail"),
]
