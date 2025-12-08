"""Run the Django admin with a local HTTP server for Electron."""
from __future__ import annotations

import argparse
import logging
import os
import sys
import shutil
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path

import appdirs

PACKAGED_ROOT = Path(__file__).resolve().parent.parent


def _get_appdata_dir() -> Path:
    override = os.getenv("GCI_DATA_DIR")
    if override:
        return Path(override)
    return Path(appdirs.user_data_dir("GCI-Admin", "GCI"))


def _get_log_dir() -> Path:
    override = os.getenv("DJANGO_LOG_DIR")
    if override:
        return Path(override)
    return Path(appdirs.user_log_dir("GCI-Admin", "GCI"))


APPDATA_DIR = _get_appdata_dir()
BACKEND_ROOT = APPDATA_DIR / "backend"

ROOT = BACKEND_ROOT
DB_PATH = BACKEND_ROOT / "database" / "db.sqlite3"
PACKAGED_DB_PATH = PACKAGED_ROOT / "database" / "db.sqlite3"

LOG_DIR = _get_log_dir()
LOG_FILE = LOG_DIR / "desktop_admin.log"


def ensure_database_path() -> None:
    BACKEND_ROOT.mkdir(parents=True, exist_ok=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if PACKAGED_DB_PATH.exists() and not DB_PATH.exists():
        shutil.copy2(PACKAGED_DB_PATH, DB_PATH)
        logging.info("Copied initial database from %s to %s", PACKAGED_DB_PATH, DB_PATH)


# Copy backend tree from packaged location to AppData backend on first run
def ensure_backend_tree() -> None:
    """Ensure backend code is available under BACKEND_ROOT.

    On first run, copy the packaged backend tree (app, config, desktop_admin,
    static, templates) from PACKAGED_ROOT into BACKEND_ROOT. Subsequent runs
    will reuse the AppData copy to avoid modifying files under resources/.
    """
    BACKEND_ROOT.mkdir(parents=True, exist_ok=True)
    for name in ("app", "config", "desktop_admin", "static", "templates"):
        src = PACKAGED_ROOT / name
        dst = BACKEND_ROOT / name
        if src.exists() and not dst.exists():
            try:
                shutil.copytree(src, dst)
                logging.info("Copied backend folder %s -> %s", src, dst)
            except Exception:
                logging.exception("Failed to copy backend folder %s -> %s", src, dst)
                raise


def setup_logging() -> Path:
    global LOG_DIR, LOG_FILE

    log_dir = LOG_DIR
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        fallback_dir = Path(tempfile.gettempdir()) / "gci-admin-logs"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        print(
            f"WARNING: Could not create log directory {LOG_DIR}: {exc}. "
            f"Using fallback {fallback_dir}",
            file=sys.stderr,
            flush=True,
        )
        log_dir = fallback_dir

    LOG_DIR = log_dir
    LOG_FILE = log_dir / "desktop_admin.log"
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
    return LOG_FILE


def bootstrap_django() -> None:
    logging.info("Bootstrapping Django. ROOT=%s", ROOT)
    sys.path.insert(0, str(BACKEND_ROOT))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    ensure_backend_tree()
    ensure_database_path()
    logging.info("Ensured database path exists: %s", DB_PATH)
    try:
        import django
    except Exception:
        logging.exception(
            "Unable to import Django. Ensure the bundled environment is installed."
        )
        raise
    django.setup()
    logging.info("Django setup completed.")


def run_server(port: int) -> None:
    from django.core.management import call_command

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
    log_file = setup_logging()
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
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(
            f"FATAL: {e}\nLog file: {log_file}",
            file=sys.stderr,
            flush=True,
        )
        logging.exception("Fatal error while starting Django admin server.")
        raise

if __name__ == "__main__":
    main()
