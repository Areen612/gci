from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from app.models import Customer


BABY_BLUE = "#4da6ff"


class CustomerTable(QTableWidget):

    customer_clicked = Signal(str)          # name click
    view_invoices_clicked = Signal(str)     # "View invoices" click

    def __init__(self, show_invoice_columns=True):
        super().__init__(0, 5)
        self.setHorizontalHeaderLabels(["Name", "Email", "Phone", "Invoices", "View Invoices"])

        if not show_invoice_columns:
            self.setColumnHidden(3, True)
            self.setColumnHidden(4, True)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)

        self.setColumnWidth(0, 250)
        self.setColumnWidth(1, 200)
        self.setColumnWidth(2, 150)
        self.setColumnWidth(3, 90)
        self.setColumnWidth(4, 130)

        # Allow itemClick to detect clicks on specific columns
        self.itemClicked.connect(self.on_item_clicked)

    # ─────────────────────────────────────────
    # LOAD TABLE DATA
    # ─────────────────────────────────────────
    def load_customers(self, queryset=None):
        queryset = queryset or Customer.objects.all()

        self.setRowCount(0)
        for c in queryset:
            row = self.rowCount()
            self.insertRow(row)

            # NAME — clickable link
            name_item = QTableWidgetItem(c.name)
            name_item.setData(Qt.UserRole, str(c.id))
            name_item.setForeground(QColor(BABY_BLUE))
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.setItem(row, 0, name_item)

            # EMAIL
            email_item = QTableWidgetItem(c.email or "—")
            email_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, email_item)

            # PHONE
            phone_item = QTableWidgetItem(c.phone_number or "—")
            phone_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, phone_item)

            # INVOICE COUNT
            invoice_count = c.invoices.count()
            invoice_item = QTableWidgetItem(str(invoice_count))
            invoice_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 3, invoice_item)

            # VIEW INVOICES — clickable link
            view_item = QTableWidgetItem("View Invoices")
            view_item.setData(Qt.UserRole, str(c.id))
            view_item.setForeground(QColor(BABY_BLUE))
            view_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 4, view_item)

    # ─────────────────────────────────────────
    # SIGNAL EMISSION BASED ON CLICKED COLUMN
    # ─────────────────────────────────────────
    def on_item_clicked(self, item):
        col = item.column()
        customer_id = item.data(Qt.UserRole)
        if not customer_id:
            return

        if col == 0:
            self.customer_clicked.emit(customer_id)
        elif col == 4:
            self.view_invoices_clicked.emit(customer_id)

    # ─────────────────────────────────────────
    # SELECTION HELPER
    # ─────────────────────────────────────────
    def selected_customer_id(self):
        row = self.currentRow()
        if row < 0:
            return None
        return str(self.item(row, 0).data(Qt.UserRole))