# desktop_app/main.py
from pathlib import Path
import sys
import os

from django.conf import settings

# Add project root to Python path FIRST
ROOT = Path(__file__).resolve().parents[1]   # /gci
sys.path.insert(0, str(ROOT))  # Must be before any gci imports

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Now import Django
import django
django.setup()

# Import Qt after Django setup
from PySide6.QtWidgets import QApplication

# Import UI after Django is ready
from ui.main_window import MainWindow

# print("USING DB:", settings.DATABASES["default"]["NAME"])
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()