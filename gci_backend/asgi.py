"""ASGI config for gci_backend project."""

from __future__ import annotations

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gci_backend.settings")

application = get_asgi_application()
