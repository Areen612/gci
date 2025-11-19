from rest_framework.generics import ListAPIView
from app.models.invoice import Invoice
from app.serializers.invoice_serializers import InvoiceSerializer

class InvoiceListView(ListAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer