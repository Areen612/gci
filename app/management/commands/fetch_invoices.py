from django.core.management.base import BaseCommand
from app.services.jofoatara_api import JofoataraClient
from app.services.invoice_logic import process_invoice_payload
from django.db import transaction

class Command(BaseCommand):
    help = "Fetch and store all invoices into the DB"

    def handle(self, *args, **kwargs):
        client = JofoataraClient()

        try:
            self.stdout.write("➡️ Logging in…")
            client.login()
            self.stdout.write("✔ Logged in.")
        except Exception as e:
            self.stderr.write(f"❌ Login failed: {e}")
            return

        try:
            self.stdout.write("➡️ Fetching invoice list…")
            invoices = client.fetch_all_invoices()
            self.stdout.write(f"✔ {len(invoices)} invoices found.")
        except Exception as e:
            self.stderr.write(f"❌ Failed to fetch invoice list: {e}")
            return

        for inv in invoices:
            try:
                self.stdout.write(f"➡️ Fetching details for invoice {inv['invoiceNumber']}...")
                full = client.fetch_invoice(inv["invoiceUniqueIdentifier"], inv["invoiceNumber"])
                if not full:
                    self.stdout.write(f"⚠ Skipped invoice {inv['invoiceNumber']}: missing customer name")
                    continue

                with transaction.atomic():
                    process_invoice_payload(full)
                    self.stdout.write(f"✔ Processed invoice {inv['invoiceNumber']}")
            except Exception as e:
                self.stderr.write(f"❌ Failed to process invoice {inv['invoiceNumber']}: {e}")

        self.stdout.write(self.style.SUCCESS("🎉 All invoices processed successfully"))