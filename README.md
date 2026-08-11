# IDOR Student Document Portal

An educational Flask project that will demonstrate and prevent insecure direct
object reference (IDOR) vulnerabilities using fictional student data.

> This project is for a controlled local security demonstration. It must not be
> deployed publicly or used with real personal information.

## Current milestone

Phase 2.2 is complete: the project includes a minimal Flask application, a home
route, an HTML template, and basic styling. The database will be implemented in
the next step.

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
python -c "from importlib.metadata import version; print(version('flask'))"
```

The expected Flask version for this milestone is `3.1.3`.

## Run the application

Make sure the virtual environment is active, then run:

```powershell
python app.py
```

The terminal should display a local address similar to:

```text
http://127.0.0.1:5000
```

Hold `Ctrl` and click the address, or copy it into a web browser. You should see
the Student Document Portal home page.

Keep the terminal open while using the application. To stop the Flask server,
return to the terminal and press `Ctrl+C`.

## Files used in Phase 2.2

- `app.py` creates the Flask application and handles the `/` route.
- `templates/home.html` defines the page shown in the browser.
- `static/style.css` controls the page's appearance.

## Leave the virtual environment

```bash
deactivate
```

The `.venv` directory is intentionally excluded from Git and shared project
archives. Each developer creates it locally using the commands above.
