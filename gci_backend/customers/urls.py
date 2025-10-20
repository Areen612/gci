from django.urls import path

from .views import CustomerCreateView, CustomerDetailView, CustomerListView

app_name = "customers"

urlpatterns = [
    path("", CustomerListView.as_view(), name="list"),
    path("create/", CustomerCreateView.as_view(), name="create"),
    path("<int:pk>/", CustomerDetailView.as_view(), name="detail"),
]
