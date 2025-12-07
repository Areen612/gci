"""Run the Django admin with a local HTTP server for Electron."""
from __future__ import annotations

import argparse
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import django
from django.core.management import call_command

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "desktop_app" / "database" / "db.sqlite3"
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "desktop_admin.log"


def ensure_database_path() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def setup_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1_000_000,  # ~1 MB
        backupCount=3,
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    # Also log to stderr so Electron sees something in its console
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)
    root_logger.addHandler(stderr_handler)

    logging.info("Logging initialized. Log file: %s", LOG_FILE)


def bootstrap_django() -> None:
    logging.info("Bootstrapping Django. ROOT=%s", ROOT)
    sys.path.insert(0, str(ROOT))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    ensure_database_path()
    logging.info("Ensured database path exists: %s", DB_PATH)
    django.setup()
    logging.info("Django setup completed.")


def run_server(port: int) -> None:
    logging.info("Running migrations...")
    call_command("migrate", interactive=False, verbosity=1)
    logging.info("Migrations completed.")

    logging.info("Starting Django development server on 127.0.0.1:%s", port)
    call_command(
        "runserver",
        f"127.0.0.1:{port}",
        use_reloader=False,
        insecure_serving=True,
    )


def main(argv: list[str] | None = None) -> None:
    setup_logging()
    logging.info("admin_server main() starting. argv=%s", argv)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("DJANGO_PORT", "8765")),
    )
    args = parser.parse_args(argv)

    try:
        bootstrap_django()
        logging.info(
            "Django admin running at http://127.0.0.1:%s/admin/",
            args.port,
        )
        print(
          f"Django admin running at http://127.0.0.1:{args.port}/admin/",
          flush=True,
        )
        run_server(args.port)
    except Exception:
        logging.exception("Fatal error while starting Django admin server.")
        # Make sure something visible goes to Electron stderr as well
        print("Fatal error in admin_server.py, see log file for details.", file=sys.stderr, flush=True)
        raise


if __name__ == "__main__":
    main()