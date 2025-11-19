# app/management/commands/sync_jofotara.py
import os
import base64
from datetime import datetime
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
import requests

from app.models import Seller, Buyer, Invoice, InvoiceItem

JOFOTARA_LOGIN_URL = os.environ.get("JOFOTARA_LOGIN_URL", "https://portal.jofotara.gov.jo/login")
# This is example; replace with actual login post URL if different
JOFOTARA_INVOICE_URL_TEMPLATE = os.environ.get(
    "JOFOTARA_INVOICE_URL_TEMPLATE",
    "https://backend.jofotara.gov.jo/sme/invoices/{uuid}/{invoice_number}"
)

USERNAME = os.environ.get("JOFOTARA_USERNAME")
PASSWORD = os.environ.get("JOFOTARA_PASSWORD")
TAX_NUMBER = os.environ.get("JOFOTARA_TAX_NUMBER")  # optional use

class Command(BaseCommand):
    help = "Sync invoices from JOFotara for the configured account."

    def sync_invoices(self, *args, **options):
        if not USERNAME or not PASSWORD:
            self.stdout.write(self.style.ERROR("Set JOFOTARA_USERNAME and JOFOTARA_PASSWORD env vars"))
            return

        session = requests.Session()
        session.headers.update({"User-Agent": "MyDjangoApp/1.0"})

        # === 1) Login flow
        # 1a) Get login page (in case CSRF token is required)
        try:
            r = session.get(JOFOTARA_LOGIN_URL, timeout=15)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Cannot reach login page: {e}"))
            return

        # If the portal uses a CSRF token in the form, you must extract it from `r.text` and include in login_data.
        # For many portals you can simply POST credentials to the login endpoint.
        login_payload = {
            "username": USERNAME,
            "password": PASSWORD,
            # add csrf token here if needed: "csrfmiddlewaretoken": "<value>"
        }
        # Replace the below URL with the actual POST login endpoint if different:
        login_post_url = os.environ.get("JOFOTARA_LOGIN_POST_URL", JOFOTARA_LOGIN_URL)

        resp = session.post(login_post_url, data=login_payload, timeout=15)
        if resp.status_code not in (200, 302):
            self.stdout.write(self.style.ERROR(f"Login failed: {resp.status_code}"))
            return

        self.stdout.write(self.style.SUCCESS("Logged in to portal successfully."))

        # === 2) Fetch invoice(s)
        # If you already know the invoice UUID and number, substitute them. If you need a list, implement list endpoint calls.
        # Example: fetch single invoice (replace with loop over invoice list)
        example_uuid = "5b7bc5bb-5f0f-449b-b9dc-a84ad255a7cb"
        example_invoice_number = "EIN00904"
        invoice_url = JOFOTARA_INVOICE_URL_TEMPLATE.format(uuid=example_uuid, invoice_number=example_invoice_number)

        jresp = session.get(invoice_url, timeout=15)
        if jresp.status_code != 200:
            self.stdout.write(self.style.ERROR(f"Failed to fetch invoice: {jresp.status_code}"))
            return

        data = jresp.json()

        # === 3) Persist
        with transaction.atomic():
            seller_info = data.get("sellerDTO", {})
            seller, _ = Seller.objects.get_or_create(
                tax_number=seller_info.get("taxNumber") or "",
                defaults={
                    "name": seller_info.get("name"),
                    "mobile": seller_info.get("mobileNumber")
                }
            )

            buyer_info = data.get("buyerDTO", {})
            buyer, _ = Buyer.objects.get_or_create(
                name=buyer_info.get("buyerName") or "Unknown",
                defaults={"additional_id": buyer_info.get("additionalBuyerId")}
            )

            # Parse date format "09-11-2025" -> day-month-year
            issue_date_raw = data.get("issueDate")
            try:
                issue_date = datetime.strptime(issue_date_raw, "%d-%m-%Y").date() if issue_date_raw else None
            except Exception:
                issue_date = None

            invoice_obj, created = Invoice.objects.update_or_create(
                uuid=data.get("invoiceUniqueIdentifier"),
                defaults={
                    "invoice_number": data.get("invoiceNumber"),
                    "issue_date": issue_date,
                    "currency": data.get("currencyEnum"),
                    "total_payable": data.get("totalPayableAmount") or 0,
                    "total_excl_taxes": data.get("totalAmountExcludingTaxes"),
                    "xml": data.get("xml"),
                    "qr_base64": data.get("qrCodeImage"),
                    "seller": seller,
                    "buyer": buyer,
                }
            )

            # Save QR image from base64 if present
            qr_b64 = data.get("qrCodeImage")  # format: "data:image/png;base64,...."
            if qr_b64:
                if qr_b64.startswith("data:image"):
                    header, b64data = qr_b64.split(",", 1)
                else:
                    b64data = qr_b64
                try:
                    img_data = base64.b64decode(b64data)
                    filename = f"{invoice_obj.invoice_number}_qr.png"
                    invoice_obj.qr_image.save(filename, ContentFile(img_data), save=False)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Failed to decode/save QR image: {e}"))

            invoice_obj.save()

            # Items
            InvoiceItem.objects.filter(invoice=invoice_obj).delete()  # simple approach: wipe and re-add
            items = data.get("invoiceItemDTOList", [])
            for it in items:
                InvoiceItem.objects.create(
                    invoice=invoice_obj,
                    product_description=it.get("productDescription", "")[:512],
                    quantity=it.get("quantity") or None,
                    unit_price=it.get("unitPrice") or None,
                    total_amount=it.get("subtotalAmount") or None
                )

        self.stdout.write(self.style.SUCCESS(f"Invoice {invoice_obj.invoice_number} synced."))
        

