from PySide6.QtCore import Qt, Signal
from PySide6 import QtGui
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem
from app.models import Customer

BABY_BLUE = "#4da6ff"


class CustomerTable(QTableWidget):

    # name click → customer details
    customer_clicked = Signal(str)
    # “View invoices” click → invoice list
    view_invoices_clicked = Signal(str)

    def __init__(self, show_invoice_columns=True):
        super().__init__(0, 5)

        self.setHorizontalHeaderLabels(
            ["Name", "Email", "Phone", "Invoices", "View Invoices"]
        )

        if not show_invoice_columns:
            # Hide "Invoices" and "View Invoices" columns (3, 4)
            self.setColumnHidden(3, True)
            self.setColumnHidden(4, True)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.itemClicked.connect(self.on_item_clicked)

    # ── Load customers into table ──────────────────────────────────────
    def load_customers(self, queryset=None):
        queryset = queryset or Customer.objects.all()

        self.setRowCount(0)
        for c in queryset:
            row = self.rowCount()
            self.insertRow(row)

            # Name (clickable)
            name_item = QTableWidgetItem(c.name)
            name_item.setData(Qt.UserRole, str(c.id))
            name_item.setForeground(QtGui.QColor(BABY_BLUE))
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.setItem(row, 0, name_item)

            # Email
            email_item = QTableWidgetItem(c.email or "—")
            email_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, email_item)

            # Phone
            phone_item = QTableWidgetItem(c.phone_number or "—")
            phone_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, phone_item)

            # Invoice count
            invoice_count = c.invoices.count()
            invoice_item = QTableWidgetItem(str(invoice_count))
            invoice_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 3, invoice_item)

            # “View Invoices” (clickable)
            view_item = QTableWidgetItem("View Invoices")
            view_item.setData(Qt.UserRole, str(c.id))
            view_item.setForeground(QtGui.QColor(BABY_BLUE))
            view_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 4, view_item)

    # ── Click handling ─────────────────────────────────────────────────
    def on_item_clicked(self, item: QTableWidgetItem):
        col = item.column()
        customer_id = item.data(Qt.UserRole)
        if not customer_id:
            return

        if col == 0:
            # Name clicked → customer details
            self.customer_clicked.emit(customer_id)
        elif col == 4:
            # “View Invoices” clicked → invoice list
            self.view_invoices_clicked.emit(customer_id)

    # ── Helper for “View Customer Details” button (if you still use it) ─
    def selected_customer_id(self):
        row = self.currentRow()
        if row < 0:
            return None
        item = self.item(row, 0)
        if not item:
            return None
        return str(item.data(Qt.UserRole))
