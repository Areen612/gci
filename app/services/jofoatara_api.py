import os
import requests
from django.conf import settings


class JofoataraClient:
    BASE_URL = os.getenv("JOFOTARA_BASE_URL", "https://backend.jofotara.gov.jo")

    LOGIN_ENDPOINT = "/users/auth/login"
    INVOICE_LIST_ENDPOINT = "/sme/invoices/"
    INVOICE_DETAILS_ENDPOINT = "/sme/invoices/{uuid}/{number}"

    def __init__(self):
        self.tax_number = os.getenv("JOFOTARA_TAX_NUMBER")
        self.username = os.getenv("JOFOTARA_USERNAME")
        self.password = os.getenv("JOFOTARA_PASSWORD")

        self.session = requests.Session()
        self.access_token = None

    # --------------------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------------------
    def login(self):
        url = self.BASE_URL + self.LOGIN_ENDPOINT
        payload = {
            "taxNumber": self.tax_number,
            "username": self.username,
            "password": self.password,
        }

        response = self.session.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15,
        )

        if response.status_code != 200:
            raise Exception(f"Login failed: {response.status_code} {response.text}")

        data = response.json()
        self.access_token = data.get("access_token")

        if not self.access_token:
            raise Exception("Login succeeded but no access_token returned.")

        self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
        return True

    # --------------------------------------------------------------------
    # FETCH INVOICE LIST (Paginated)
    # --------------------------------------------------------------------
    def fetch_invoice_list(self, page=1):
        url = self.BASE_URL + self.INVOICE_LIST_ENDPOINT
        params = {"page": page}

        response = self.session.get(url, params=params, timeout=15)
        response.raise_for_status()

        return response.json()
    
    
    # --------------------------------------------------------------------
    # FETCH ALL INVOICES (Handles Pagination)
    # --------------------------------------------------------------------
    def fetch_all_invoices(self):
        page = 1
        all_items = []

        while True:
            data = self.fetch_invoice_list(page=page)
            items = data.get("invoiceList", [])
            if not items:
                break  # No more pages

            all_items.extend(items)
            page += 1

        return all_items

    # --------------------------------------------------------------------
    # FETCH INVOICE DETAILS
    # --------------------------------------------------------------------
    def fetch_invoice(self, uuid, number):
        url = self.BASE_URL + self.INVOICE_DETAILS_ENDPOINT.format(
            uuid=uuid,
            number=number,
        )

        response = self.session.get(url, timeout=15)
        response.raise_for_status()

        return response.json()