from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

from app.models import Invoice


class InvoiceDetailsDialog(QDialog):
    def __init__(self, invoice_id: str, parent=None):
        super().__init__(parent)

        invoice = (
            Invoice.objects.select_related("customer", "seller")
            .prefetch_related("line_items__item")
            .get(id=invoice_id)
        )

        self.setWindowTitle(f"Invoice {invoice.invoice_number}")
        self.setMinimumWidth(820)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"<b>Invoice #:</b> {invoice.invoice_number}"))
        layout.addWidget(
            QLabel(
                f"<b>Customer:</b> {invoice.customer.name if invoice.customer else '—'}"
            )
        )
        layout.addWidget(QLabel(f"<b>Status:</b> {invoice.get_status_display()}"))
        layout.addWidget(QLabel(f"<b>Issue date:</b> {invoice.issue_date}"))
        layout.addWidget(QLabel(f"<b>Total due:</b> {invoice.total_due}"))

        # Line items table
        table = QTableWidget(0, 6, self)
        table.setHorizontalHeaderLabels(
            [
                "Item",
                "Qty",
                "Unit price",
                "Discount",
                "Line subtotal",
                "Total after discount",
            ]
        )
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for line in invoice.line_items.all():
            row = table.rowCount()
            table.insertRow(row)

            item_name = line.item.name if line.item else (line.item_name or "—")
            table.setItem(row, 0, QTableWidgetItem(item_name))
            table.setItem(row, 1, QTableWidgetItem(str(line.quantity)))
            table.setItem(row, 2, QTableWidgetItem(str(line.unit_price)))
            table.setItem(row, 3, QTableWidgetItem(str(line.discount_amount)))
            table.setItem(row, 4, QTableWidgetItem(str(line.line_subtotal)))
            table.setItem(
                row,
                5,
                QTableWidgetItem(
                    "" if line.total_after_discount is None else str(line.total_after_discount)
                ),
            )

        layout.addWidget(table)
