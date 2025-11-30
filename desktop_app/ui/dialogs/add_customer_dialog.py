from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QMessageBox,
)

from app.models import Customer


class AddCustomerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Customer")
        self.setMinimumWidth(420)

        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()
        self.postal_code_input = QLineEdit()
        self.additional_id_input = QLineEdit()

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.addRow("Name*:", self.name_input)
        form.addRow("Email:", self.email_input)
        form.addRow("Phone:", self.phone_input)
        form.addRow("Additional ID:", self.additional_id_input)
        form.addRow("Address:", self.address_input)
        form.addRow("Postal code:", self.postal_code_input)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_customer)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.created_customer = None

    def save_customer(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing name", "Customer name is required.")
            return

        customer_data = {
            "name": name,
            "email": self.email_input.text().strip() or None,
            "phone_number": self.phone_input.text().strip() or None,
            "address": self.address_input.text().strip() or None,
            "postal_code": self.postal_code_input.text().strip() or None,
            "additional_id": self.additional_id_input.text().strip() or None,
        }

        try:
            self.created_customer = Customer.objects.create(**customer_data)
        except Exception as exc:  # pragma: no cover - UI validation path
            QMessageBox.critical(self, "Could not save", str(exc))
            self.created_customer = None
            return

        self.accept()
