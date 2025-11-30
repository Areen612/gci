from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from app.models import Invoice

BABY_BLUE = "#4da6ff"


class InvoicesPageDialog(QDialog):

    invoice_clicked = Signal(str)  # invoice UUID

    def __init__(self, customer_id: str):
        super().__init__()
        self.setWindowTitle("Customer Invoices")
        self.setMinimumWidth(900)

        layout = QVBoxLayout()

        # Table with all invoice fields
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Invoice Number",
            "Customer",
            "Status",
            "Issue Date",
            "Subtotal",
            "Discount",
            "Total Due"
        ])
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 120)

        self.table.itemClicked.connect(self.handle_item_click)

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_invoices(customer_id)

    # ─────────────────────────────────────────────
    def load_invoices(self, customer_id):
        queryset = Invoice.objects.filter(customer_id=customer_id).order_by("-issue_date")

        for inv in queryset:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Invoice number (clickable baby blue)
            inv_item = QTableWidgetItem(inv.invoice_number)
            inv_item.setForeground(QColor(BABY_BLUE))
            inv_item.setData(Qt.UserRole, str(inv.uuid))
            self.table.setItem(row, 0, inv_item)

            self.table.setItem(row, 1, QTableWidgetItem(inv.customer.name if inv.customer else "—"))
            self.table.setItem(row, 2, QTableWidgetItem(inv.status))
            self.table.setItem(row, 3, QTableWidgetItem(str(inv.issue_date)))
            self.table.setItem(row, 4, QTableWidgetItem(str(inv.subtotal)))
            self.table.setItem(row, 5, QTableWidgetItem(str(inv.discount_total)))
            self.table.setItem(row, 6, QTableWidgetItem(str(inv.total_due)))

    # ─────────────────────────────────────────────
    def handle_item_click(self, item):
        if item.column() == 0:  # Invoice Number clicked
            invoice_uuid = item.data(Qt.UserRole)
            if invoice_uuid:
                self.open_invoice_details(invoice_uuid)

    # def open_invoice_details(self, invoice_uuid: str):
    #     from .invoice_details import InvoiceDetailsDialog
    #     dlg = InvoiceDetailsDialog(invoice_uuid)
    #     dlg.exec()