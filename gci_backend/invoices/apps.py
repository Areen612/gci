from django.apps import AppConfig


class InvoicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "gci_backend.invoices"

    def ready(self) -> None:
        from . import signals  # noqa: F401
