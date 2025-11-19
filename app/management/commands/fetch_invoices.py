from django.core.management.base import BaseCommand
from app.services.jofoatara_api import sync_invoices

class Command(BaseCommand):
    help = "Fetch invoice data from Jofoatara API"

    def handle(self, *args, **kwargs):
        sync_invoices()
        self.stdout.write(self.style.SUCCESS("Invoices synced successfully"))