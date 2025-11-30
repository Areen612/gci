from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, QTimer
from app.models import Customer


class CustomerSearchBar(QWidget):
    customer_selected = Signal(str)

    def __init__(self):
        super().__init__()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search customers…")
        self.search_input.textChanged.connect(self._delayed_search)

        self.suggestions = QListWidget()
        self.suggestions.hide()
        self.suggestions.itemClicked.connect(self._select_customer)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.search_input)
        layout.addWidget(self.suggestions)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._search_db)

    def _delayed_search(self):
        self.timer.start(150)   # debounce: 150ms

    def _search_db(self):
        text = self.search_input.text().strip()
        self.suggestions.clear()

        if not text:
            self.suggestions.hide()
            return

        matches = Customer.objects.filter(name__istartswith=text)[:10]

        for c in matches:
            item = QListWidgetItem(f"{c.name} — {c.phone_number or 'no phone'}")
            item.setData(Qt.UserRole, c.id)
            self.suggestions.addItem(item)

        if matches:
            self.suggestions.show()
        else:
            self.suggestions.hide()

    def _select_customer(self, item):
        customer_id = item.data(Qt.UserRole)
        self.customer_selected.emit(str(customer_id))
        self.suggestions.hide()
        self.search_input.clear()