# IDOR Student Document Portal

An educational Flask project that will demonstrate and prevent insecure direct
object reference (IDOR) vulnerabilities using fictional student data.

> This project is for a controlled local security demonstration. It must not be
> deployed publicly or used with real personal information.

## Current milestone

Phase 2.1 is complete: the Python environment and starter project structure are
prepared. The application routes and database will be implemented in the next
steps.

## Requirements

- Python 3.10 or newer
- `pip`

SQLite support is included with Python, so no separate database server or
SQLite package is required.

## Set up the project

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

After activation, the terminal prompt normally begins with `(.venv)`.

## Check the installation

```bash
python -c "import flask; print(flask.__version__)"
```

The expected Flask version for this milestone is `3.1.3`.

## Leave the virtual environment

```bash
deactivate
```

The `.venv` directory is intentionally excluded from Git and shared project
archives. Each developer creates it locally using the commands above.
