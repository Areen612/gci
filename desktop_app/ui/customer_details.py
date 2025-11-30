from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QFormLayout,
    QWidget,
    QHeaderView,
)

from app.models import Customer


class CustomerDetailsDialog(QDialog):
    """Detailed view for a single customer with recent invoices."""

    def __init__(self, customer_id, parent=None):
        super().__init__(parent)

        customer = Customer.objects.prefetch_related("invoices").get(id=customer_id)

        self.setWindowTitle(f"Customer – {customer.name}")
        self.setMinimumWidth(760)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # ── Customer header & info panel ───────────────────────────────
        layout.addWidget(QLabel(f"<h2 style='margin:0'>{customer.name}</h2>"))

        info_panel = QWidget(self)
        info_layout = QFormLayout(info_panel)
        info_layout.setLabelAlignment(Qt.AlignLeft)
        info_layout.setFormAlignment(Qt.AlignLeft)
        info_layout.setHorizontalSpacing(12)
        info_layout.setVerticalSpacing(6)

        info_layout.addRow("Email:", QLabel(customer.email or "—"))
        info_layout.addRow("Phone:", QLabel(customer.phone_number or "—"))
        info_layout.addRow("Address:", QLabel(customer.address or "—"))
        info_layout.addRow("Preferred contact:", QLabel(customer.preferred_contact_method))
        info_layout.addRow("Loyalty status:", QLabel(customer.loyalty_status))

        layout.addWidget(info_panel)

        # ── Invoices table ─────────────────────────────────────────────
        invoices_label = QLabel("<b>Invoices</b>")
        invoices_label.setAlignment(Qt.AlignVCenter)
        layout.addWidget(invoices_label)

        self.invoice_table = QTableWidget(0, 4, self)
        self.invoice_table.setHorizontalHeaderLabels(
            ["Invoice Number", "Status", "Issue date", "Total due"]
        )
        self.invoice_table.verticalHeader().setVisible(True)
        self.invoice_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.invoice_table.setSelectionMode(QTableWidget.NoSelection)
        header = self.invoice_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setDefaultAlignment(Qt.AlignCenter)

        for inv in customer.invoices.order_by("-issue_date", "-invoice_number"):
            row = self.invoice_table.rowCount()
            self.invoice_table.insertRow(row)

            number_item = QTableWidgetItem(inv.invoice_number)
            number_item.setTextAlignment(Qt.AlignCenter)
            self.invoice_table.setItem(row, 0, number_item)

            status_item = QTableWidgetItem(inv.get_status_display())
            status_item.setTextAlignment(Qt.AlignCenter)
            self.invoice_table.setItem(row, 1, status_item)

            date_text = inv.issue_date.strftime("%b %d, %Y") if inv.issue_date else "—"
            date_item = QTableWidgetItem(date_text)
            date_item.setTextAlignment(Qt.AlignCenter)
            self.invoice_table.setItem(row, 2, date_item)

            total_item = QTableWidgetItem(f"{inv.total_due:.6f}")
            total_item.setTextAlignment(Qt.AlignCenter)
            self.invoice_table.setItem(row, 3, total_item)

        layout.addWidget(self.invoice_table)
