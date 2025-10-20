from __future__ import annotations

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from .forms import CustomerForm
from .models import Customer


class CustomerListView(View):
    template_name = "customers/customer_list.html"

    def get(self, request):
        customers = Customer.objects.order_by("last_name", "first_name")
        return render(request, self.template_name, {"customers": customers})


class CustomerCreateView(View):
    template_name = "customers/customer_form.html"

    def get(self, request):
        form = CustomerForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, "Customer created successfully.")
            return redirect(reverse("customers:detail", args=[customer.pk]))
        return render(request, self.template_name, {"form": form})


class CustomerDetailView(View):
    template_name = "customers/customer_detail.html"

    def get(self, request, pk: int):
        customer = get_object_or_404(Customer, pk=pk)
        return render(request, self.template_name, {"customer": customer})
