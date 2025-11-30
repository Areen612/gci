from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PySide6.QtCore import Qt

from .navigation import NavigationSidebar
from .dashboard_page import DashboardPage
from .customers_page import CustomersPage
from .invoices_page import InvoicesPage


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GCI Manager")
        self.setMinimumSize(1200, 800)

        # Layout
        container = QWidget()
        self.layout = QHBoxLayout()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Sidebar
        self.sidebar = NavigationSidebar()
        self.sidebar.page_changed.connect(self.switch_page)
        self.layout.addWidget(self.sidebar)

        # Default page
        self.current_page = None
        self.switch_page("dashboard")

    def switch_page(self, page_name):
        if self.current_page:
            self.layout.removeWidget(self.current_page)
            self.current_page.deleteLater()

        if page_name == "dashboard":
            self.current_page = DashboardPage()
        elif page_name == "customers":
            self.current_page = CustomersPage()
        elif page_name == "invoices":
            self.current_page = InvoicesPage()

        self.layout.addWidget(self.current_page)