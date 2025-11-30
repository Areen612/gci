from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
)
from PySide6.QtCore import Qt
from PySide6 import QtGui

from app.models import Customer
from ui.invoice_details import InvoiceDetailsDialog

BABY_BLUE = "#4da6ff"


class InvoicesPageDialog(QDialog):

    def __init__(self, customer_id: str, parent=None):
        super().__init__(parent)

        self.customer = Customer.objects.get(id=customer_id)
        self.setWindowTitle(f"Invoices - {self.customer.name}")
        self.setMinimumWidth(900)

        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 7, self)
        self.table.setHorizontalHeaderLabels(
            [
                "Invoice number",
                "Customer",
                "Status",
                "Issue date",
                "Subtotal",
                "Discount total",
                "Total due",
            ]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.load_invoices()
        self.table.itemClicked.connect(self.on_item_clicked)

        layout.addWidget(self.table)

    def load_invoices(self):
        invoices = (
            self.customer.invoices.select_related("customer")
            .all()
            .order_by("-issue_date", "-invoice_number")
        )

        self.table.setRowCount(0)
        for inv in invoices:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Invoice number (clickable)
            num_item = QTableWidgetItem(inv.invoice_number)
            num_item.setData(Qt.UserRole, str(inv.id))
            num_item.setForeground(QtGui.QColor(BABY_BLUE))
            num_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row, 0, num_item)

            # Customer name
            customer_name = inv.customer.name if inv.customer else "—"
            self.table.setItem(row, 1, QTableWidgetItem(customer_name))

            # Status (uses Django choices)
            status_label = inv.get_status_display()
            self.table.setItem(row, 2, QTableWidgetItem(status_label))

            # Issue date formatted similar to Django admin
            if inv.issue_date:
                date_text = inv.issue_date.strftime("%b %d, 2025") if False else inv.issue_date.strftime("%b %d, %Y")
            else:
                date_text = "—"
            self.table.setItem(row, 3, QTableWidgetItem(date_text))

            # Subtotal / discounts / total due → formatted from Decimal
            self.table.setItem(row, 4, QTableWidgetItem(f"{inv.subtotal:.3f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{inv.discount_total:.3f}"))
            self.table.setItem(row, 6, QTableWidgetItem(f"{inv.total_due:.6f}"))

    def on_item_clicked(self, item: QTableWidgetItem):
        # Only invoice number column opens details
        if item.column() != 0:
            return

        invoice_id = item.data(Qt.UserRole)
        if not invoice_id:
            return

        dlg = InvoiceDetailsDialog(invoice_id, self)
        dlg.exec()
