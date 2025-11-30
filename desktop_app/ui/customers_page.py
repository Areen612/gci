from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from .customer_details import CustomerDetailsDialog
from .dialogs.add_customer_dialog import AddCustomerDialog
from .widgets.customer_search_bar import CustomerSearchBar
from .widgets.customer_table import CustomerTable


class CustomersPage(QWidget):

    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # ── Top bar: Search + Add Customer ───────────────────────────────
        top_bar = QHBoxLayout()

        self.search_bar = CustomerSearchBar()
        self.search_bar.customer_selected.connect(self.open_customer_by_id)
        top_bar.addWidget(self.search_bar)

        add_customer_btn = QPushButton("Add Customer")
        add_customer_btn.clicked.connect(self.add_customer)
        add_customer_btn.setMinimumWidth(140)
        top_bar.addWidget(add_customer_btn)

        main_layout.addLayout(top_bar)

        # ── Customers table ─────────────────────────────────────────────
        self.table = CustomerTable(show_invoice_columns=True)
        self.table.customer_clicked.connect(self.open_customer_by_id)
        self.table.view_invoices_clicked.connect(self.open_invoices_for_customer)
        self.table.load_customers()
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

    # ── Callbacks ──────────────────────────────────────────────────────
    def open_customer_by_id(self, customer_id: str):
        dlg = CustomerDetailsDialog(customer_id)
        dlg.exec()

    def open_invoices_for_customer(self, customer_id: str):
        from ui.dialogs.invoices_dialog import InvoicesPageDialog
        dlg = InvoicesPageDialog(customer_id, self)
        dlg.exec()

    def add_customer(self):
        dialog = AddCustomerDialog(self)
        if dialog.exec():
            self.table.load_customers()
