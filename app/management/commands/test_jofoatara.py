from django.core.management.base import BaseCommand
from app.services.jofoatara_api import JofoataraClient
import json


class Command(BaseCommand):
    help = "Test Jofoatara API client"

    def handle(self, *args, **options):
        client = JofoataraClient()

        print("➡️ Logging in…")
        client.login()
        print("✔ Login success.")

        print("\n➡️ Fetching invoice list…")
        data = client.fetch_invoice_list()
        print("✔ Invoice list OK.")
        
        first = data.get("invoiceList", [])[0]
        print(f"First invoice → UUID={first['invoiceUniqueIdentifier']} NUMBER={first['invoiceNumber']}")
        
        print("\n➡️ Fetching ALL invoices...")
        all_invoices = client.fetch_all_invoices()
        print(f"✔ Retrieved {len(all_invoices)} invoices across all pages.")


        print("\n➡️ Fetching full invoice details…")
        invoice = client.fetch_invoice(
            first["invoiceUniqueIdentifier"],
            first["invoiceNumber"],
        )
        
        print("✔ Invoice details OK.")

        print("\nDone.")