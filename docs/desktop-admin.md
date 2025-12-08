# Electron + Django admin desktop shell

This repository now includes a lightweight Electron launcher that spins up the Django admin on a local HTTP port and loads it in a desktop window. The Python server runs inside the same checkout, so all admin pages and static assets stay available even when offline.

## Prerequisites

- Python 3.11+
- Node 18+ (for Electron)
- A virtual environment with the project dependencies installed (`pip install -e .` or `pip install -r requirements.txt` if present)

## First-time setup

1. Ensure the SQLite location used by `config/settings.py` is available. The Electron server will create `desktop_app/database/db.sqlite3` automatically if it is missing.
2. Apply migrations and create a superuser so you can log into the admin dashboard:

```bash
python manage.py migrate
python manage.py createsuperuser
```

## Running the desktop admin

From the repository root:

```bash
# Install Electron dependencies (once)
npm install --prefix desktop_admin/electron

# Start the bundled Django server and open the admin dashboard
npm start --prefix desktop_admin/electron
```

By default the Django process listens on `127.0.0.1:8765`. To use a different port (for example when another process is already bound), set `DJANGO_PORT` before launching Electron:

```bash
DJANGO_PORT=9000 npm start --prefix desktop_admin/electron
```

On Windows, if `python3` is not available on `PATH`, use the helper script that forces `python` as the interpreter:

```bash
npm run start:windows --prefix desktop_admin/electron
```

When you quit the Electron window, the embedded Django server will be stopped automatically.

## Logs and troubleshooting

- Django server logs are written to `%LOCALAPPDATA%/GCI/GCI-Admin/Logs/desktop_admin.log` on Windows, `~/Library/Logs/GCI-Admin/desktop_admin.log` on macOS, and `~/.cache/GCI-Admin/log/desktop_admin.log` on Linux.
- The Electron window now shows the exit code plus the last few log lines if Django stops unexpectedly.
- Override the log or data root if needed by setting `DJANGO_LOG_DIR` or `GCI_DATA_DIR` before running `npm start`/`npm run start:windows`.
