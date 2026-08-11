# IDOR Student Document Portal

An educational Flask project that will demonstrate and prevent insecure direct
object reference (IDOR) vulnerabilities using fictional student data.

> This project is for a controlled local security demonstration. It must not be
> deployed publicly or used with real personal information.

## Current milestone

Phase 2.3 is complete: the project includes a reproducible SQLite schema and a
script that loads the three fictional students and six documents defined in the
experiment scope.

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

## Initialize the fictional database

With the virtual environment active, run:

```powershell
python database.py
```

Expected output:

```text
Database initialized: ...\instance\portal.db
Users: 3
Documents: 6
```

This command creates `instance\portal.db`. Running it again resets the database
to the same fictional starting data. The generated database is excluded from
Git and project archives because anyone can recreate it using this command.

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

## Database design

SQLite stores the complete database in the generated `instance\portal.db`
file. It does not require a separate database server.

The project currently has two tables:

- `users` stores each student's ID, name, username, and password hash.
- `documents` stores each document and its owner's user ID.

The relationship is:

```text
users.id <-- documents.owner_id
```

`documents.owner_id` is a foreign key. It prevents a document from being
assigned to a user who does not exist. The passwords in the approved scope are
simple demo credentials, but the database stores only password hashes.

## Files used through Phase 2.3

- `app.py` creates the Flask application and handles the `/` route.
- `database.py` creates the database and inserts the fictional records.
- `schema.sql` defines the `users` and `documents` tables.
- `templates/home.html` defines the page shown in the browser.
- `static/style.css` controls the page's appearance.

## Leave the virtual environment

```bash
deactivate
```

The `.venv` directory is intentionally excluded from Git and shared project
archives. Each developer creates it locally using the commands above.
