from __future__ import annotations
from django import template
from django.db.models import Count
from app.models import Customer

register = template.Library()


@register.simple_tag
def loyalty_leaders():
    """Return top three customers for each loyalty status."""
    leaders = []
    for status in Customer.LoyaltyStatus:
        top_customers = (
            Customer.objects.filter(loyalty_status=status.value)
            .annotate(invoice_total=Count("invoices"))
            .order_by("-invoice_total", "name")[:3]
        )
        leaders.append({
            "status_label": status.label,
            "customers": top_customers,
        })

    return leaders