"""Run the Django admin with a local HTTP server for Electron."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import django
from django.core.management import call_command


ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "desktop_app" / "database" / "db.sqlite3"


def ensure_database_path() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def bootstrap_django() -> None:
    sys.path.insert(0, str(ROOT))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    ensure_database_path()
    django.setup()


def run_server(port: int) -> None:
    call_command("migrate", interactive=False, verbosity=1)
    call_command(
        "runserver",
        f"127.0.0.1:{port}",
        use_reloader=False,
        insecure_serving=True,
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=int(os.getenv("DJANGO_PORT", "8765")))
    args = parser.parse_args(argv)

    bootstrap_django()
    print(f"Django admin running at http://127.0.0.1:{args.port}/admin/", flush=True)
    run_server(args.port)


if __name__ == "__main__":
    main()
