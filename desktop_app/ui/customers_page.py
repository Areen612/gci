from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from .widgets.customer_search_bar import CustomerSearchBar
from .widgets.customer_table import CustomerTable
from .customer_details import CustomerDetailsDialog
from app.models import Customer


class CustomersPage(QWidget):

    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # ─────────────────────────────────────────
        # TOP BAR: Search + Add Customer Button
        # ─────────────────────────────────────────
        top_bar = QHBoxLayout()

        self.search_bar = CustomerSearchBar()
        self.search_bar.customer_selected.connect(self.open_customer_by_id)
        top_bar.addWidget(self.search_bar)

        add_customer_btn = QPushButton("Add Customer")
        add_customer_btn.clicked.connect(self.add_customer)
        top_bar.addWidget(add_customer_btn)

        main_layout.addLayout(top_bar)

        # ─────────────────────────────────────────
        # TABLE
        # ─────────────────────────────────────────
        self.table = CustomerTable(show_invoice_columns=True)
        self.table.customer_clicked.connect(self.open_customer_by_id)
        self.table.view_invoices_clicked.connect(self.open_invoices_for_customer)
        self.table.load_customers()
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

    # ─────────────────────────────────────────
    # CALLBACKS
    # ─────────────────────────────────────────
    def open_customer_by_id(self, customer_id: str):
        dlg = CustomerDetailsDialog(customer_id)
        dlg.exec()

    def open_invoices_for_customer(self, customer_id: str):
        from dialogs.customer_invoices_dialog import InvoicesPageDialog
        dlg = InvoicesPageDialog(customer_id)
        dlg.exec()

    def add_customer(self):
        # Later: open create-customer dialog
        print("Add customer clicked!")