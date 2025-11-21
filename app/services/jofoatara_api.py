import os
import requests
from django.conf import settings
from app.core.constants import USER_AGENT, REQUEST_TIMEOUT


class JofoataraClient:

    def __init__(self):
        self.username = os.getenv("JOFOTARA_USERNAME")
        self.password = os.getenv("JOFOTARA_PASSWORD")

        self.login_url = os.getenv("JOFOTARA_LOGIN_URL")
        self.login_post_url = os.getenv("JOFOTARA_LOGIN_POST_URL")
        self.invoice_base_url = os.getenv("JOFOTARA_INVOICE_URL")

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    # ---------------------------------------------------------
    # LOGIN
    # ---------------------------------------------------------
    def login(self):
        if not self.username or not self.password:
            raise Exception("Missing JOFOTARA_USERNAME or JOFOTARA_PASSWORD")

        # initial GET (may include CSRF token in future)
        self.session.get(self.login_url, timeout=REQUEST_TIMEOUT)

        payload = {
            "username": self.username,
            "password": self.password
        }

        resp = self.session.post(self.login_post_url, data=payload, timeout=REQUEST_TIMEOUT)

        if resp.status_code not in (200, 302):
            raise Exception("Login failed")

        return True

    # ---------------------------------------------------------
    # FETCH INVOICE LIST
    # ---------------------------------------------------------
    def fetch_invoice_list(self):
        """
        Replace URL when you find the real list endpoint.
        For now assume the JSON you showed earlier is the list.
        """
        url = f"{self.invoice_base_url}/list"

        resp = self.session.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()

        return resp.json()

    # ---------------------------------------------------------
    # FETCH A SINGLE INVOICE DETAILS
    # ---------------------------------------------------------
    def fetch_invoice(self, uuid, invoice_number):
        url = f"{self.invoice_base_url}/{uuid}/{invoice_number}"

        resp = self.session.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()

        return resp.json()
