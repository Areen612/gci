import os
import sys
import django

def bootstrap():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Make project importable
    sys.path.insert(0, BASE_DIR)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gci.config.settings")

    django.setup()