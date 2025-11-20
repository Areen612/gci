import base64
from datetime import datetime
from django.core.files.base import ContentFile
from django.db import transaction

from app.models import Seller, Buyer, Invoice, InvoiceLineItem, Item


def process_invoice_payload(data):
    """Convert Jofoatara JSON → Django ORM models."""

    with transaction.atomic():

        # --- Seller ---
        seller_info = data.get("sellerDTO", {})
        seller, _ = Seller.objects.get_or_create(
            tax_number=seller_info.get("taxNumber", ""),
            defaults={
                "name": seller_info.get("name", ""),
                "mobile": seller_info.get("mobileNumber", ""),
            },
        )

        # --- Buyer ---
        buyer_info = data.get("customerDTO", {})
        buyer, _ = Buyer.objects.get_or_create(
            name=buyer_info.get("customerName", "Unknown"),
            defaults={"additional_id": buyer_info.get("additionalCustomerId")},
        )

        # --- Invoice ---
        issue_date = None
        if data.get("issueDate"):
            issue_date = datetime.strptime(data["issueDate"], "%d-%m-%Y").date()

        invoice, _ = Invoice.objects.update_or_create(
            uuid=data["invoiceUniqueIdentifier"],
            defaults={
                "invoice_number": data["invoiceNumber"],
                "invoice_date": issue_date,
                "currency_name": data.get("currencyEnum"),
                "total_due": data.get("totalPayableAmount") or 0,
                "seller": seller,
                "customer": buyer,
                "xml": data.get("xml"),
                "qr_base64": data.get("qrCodeImage"),
            },
        )

        # QR image
        qr = data.get("qrCodeImage")
        if qr:
            if qr.startswith("data:image"):
                _, b64data = qr.split(",", 1)
            else:
                b64data = qr

            img_bytes = base64.b64decode(b64data)
            filename = f"{invoice.invoice_number}_qr.png"
            invoice.qr_image.save(filename, ContentFile(img_bytes), save=True)

        # --- Line Items ---
        InvoiceLineItem.objects.filter(invoice=invoice).delete()

        for line in data.get("invoiceItemDTOList", []):
            item, _ = Item.objects.get_or_create(
                name=line.get("productDescription", "Item"),
                defaults={"sku": f"SKU-{invoice.invoice_number}-{line.get('id', '0')}", "base_price": 0},
            )

            InvoiceLineItem.objects.create(
                invoice=invoice,
                item=item,
                quantity=line.get("quantity", 1),
                unit_price=line.get("unitPrice", 0),
                discount_amount=line.get("discount", 0),
                line_subtotal=line.get("subtotalAmount", 0),
            )

        return invoice