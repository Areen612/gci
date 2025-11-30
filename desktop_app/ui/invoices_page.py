from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class InvoicesPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🧾 Invoices"))
        layout.addStretch()
        self.setLayout(layout)
