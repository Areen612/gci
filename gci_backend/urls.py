from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("gci_backend.customers.urls")),
    path("invoices/", include("gci_backend.invoices.urls")),
]
