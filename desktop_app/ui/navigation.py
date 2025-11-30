# desktop_app/ui/navigation.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal


class NavigationSidebar(QWidget):
    page_changed = Signal(str)   # emits: "dashboard", "customers", "invoices"

    def __init__(self):
        super().__init__()
        self.setFixedWidth(220)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("GCI Manager")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #666;")
        layout.addWidget(divider)

        # Buttons
        btn_dashboard = self._nav_button("Dashboard", "dashboard")
        btn_customers = self._nav_button("Customers", "customers")
        btn_invoices = self._nav_button("Invoices", "invoices")

        layout.addWidget(btn_dashboard)
        layout.addWidget(btn_customers)
        layout.addWidget(btn_invoices)

        layout.addStretch()
        self.setLayout(layout)

    def _nav_button(self, text, target):
        btn = QPushButton(text)
        btn.setObjectName("sidebarButton")
        btn.setMinimumHeight(40)
        btn.clicked.connect(lambda: self.page_changed.emit(target))
        return btn