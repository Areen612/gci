from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt
from app.models import Customer


class CustomerDetailsDialog(QDialog):

    def __init__(self, customer_id):
        super().__init__()
        self.setWindowTitle("Customer Details")
        self.setMinimumWidth(600)

        customer = Customer.objects.prefetch_related("invoices").get(id=customer_id)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<b>Name:</b> {customer.name}"))
        layout.addWidget(QLabel(f"<b>Email:</b> {customer.email or '—'}"))
        layout.addWidget(QLabel(f"<b>Phone:</b> {customer.phone_number or '—'}"))

        self.invoice_table = QTableWidget(0, 3, self)
        self.invoice_table.setHorizontalHeaderLabels(["Invoice #", "Issue date", "Total due"])
        self.invoice_table.verticalHeader().setVisible(False)
        self.invoice_table.setEditTriggers(QTableWidget.NoEditTriggers)

        for inv in customer.invoices.all():
            row = self.invoice_table.rowCount()
            self.invoice_table.insertRow(row)

            self.invoice_table.setItem(row, 0, QTableWidgetItem(inv.invoice_number))
            self.invoice_table.setItem(row, 1, QTableWidgetItem(str(inv.issue_date)))
            self.invoice_table.setItem(row, 2, QTableWidgetItem(str(inv.total_due)))

        layout.addWidget(self.invoice_table)