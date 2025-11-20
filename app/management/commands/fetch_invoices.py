from django.core.management.base import BaseCommand
from app.services.jofoatara_api import JofoataraClient
from app.services.invoice_logic import process_invoice_payload


class Command(BaseCommand):
    help = "Fetch and sync invoices from Jofoatara"

    def handle(self, *args, **kwargs):
        client = JofoataraClient()

        self.stdout.write("Logging in...")
        client.login()

        invoice_list = client.fetch_invoice_list()

        self.stdout.write(f"Found {len(invoice_list)} invoices")

        for inv in invoice_list:
            payload = client.fetch_invoice(inv["uuid"], inv["invoiceNumber"])
            process_invoice_payload(payload)

        self.stdout.write(self.style.SUCCESS("Invoices synced successfully"))