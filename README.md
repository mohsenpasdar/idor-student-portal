# IDOR Student Document Portal

An educational Flask project that will demonstrate and prevent insecure direct
object reference (IDOR) vulnerabilities using fictional student data.

> This project is for a controlled local security demonstration. It must not be
> deployed publicly or used with real personal information.

## Current milestone

Phase 2.6 is complete: all three fictional students can log in, and the
protected dashboard retrieves and lists only the two documents owned by the
current signed-in student.

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

## Test the private dashboard

Open `http://127.0.0.1:5000/login` and use any fictional account:

| Name | Username | Password |
| --- | --- | --- |
| Alice Johnson | `alice` | `alice123` |
| Bob Smith | `bob` | `bob123` |
| Charlie Brown | `charlie` | `charlie123` |

A correct login redirects to `/dashboard`. The dashboard is protected: opening
it while logged out redirects to `/login`. Each account should display exactly
these document IDs:

| Account | Document IDs |
| --- | --- |
| Alice | `1`, `2` |
| Bob | `3`, `4` |
| Charlie | `5`, `6` |

Use **Log out** in the page header, then sign in as another student to confirm
that the dashboard list changes with the account.

The browser receives a signed session cookie containing only the user's numeric
ID. It does not contain the password or password hash. If `PORTAL_SECRET_KEY` is
not configured, the app generates a temporary random signing key when it
starts. This is convenient and safe for a local demonstration, but it means
existing sessions end whenever the server restarts.

The session cookie is also marked `HttpOnly` and `SameSite=Lax`. The `Secure`
setting is intentionally not enabled because this controlled app uses local
HTTP rather than HTTPS.

The login form retrieves the submitted username using a parameterized query and
uses Werkzeug's `check_password_hash()` to verify the password against the hash
stored in SQLite. Its error message does not reveal whether the username or the
password was incorrect.

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

## Flask database access

During a request, `get_database()` opens one SQLite connection and stores it in
Flask's request context. Every query in that request reuses the same connection.
Flask automatically calls `close_database()` when the request ends.

The reusable query functions are:

- `get_user_by_id(user_id)`
- `get_user_by_username(username)`
- `get_documents_by_owner(owner_id)`
- `get_document_by_id(document_id)`

Each function uses SQL placeholders (`?`) instead of inserting input directly
into an SQL string. This keeps the queries parameterized and avoids introducing
SQL injection into the IDOR experiment.

The application uses `get_user_by_username()` during login and
`get_user_by_id()` to load the signed-in user at the start of each request.

## Session-based authentication and dashboard filtering

- `load_logged_in_user()` reads `user_id` from the signed session and loads the
  matching database user into Flask's request-local `g` object.
- `login_required` protects routes that should only be available to an
  authenticated student.
- `/login` verifies the submitted credentials and creates the session.
- `/logout` clears the session and returns to the public home page.
- `/dashboard` passes `g.user["id"]` to `get_documents_by_owner()` and sends the
  resulting rows to `dashboard.html`.
- `dashboard.html` loops over those rows and displays each document's type,
  title, and numeric ID.

The dashboard query includes `owner_id`, so one student's list cannot contain
another student's documents. Authentication answers **who the user is**, while
this owner-filtered query controls which records appear in the dashboard.

The dashboard does not yet open individual documents. The document-view route
and its intentional object-level authorization flaw will be added separately,
as defined in the approved experiment scope.

## Files used through Phase 2.6

- `app.py` creates Flask and handles authentication, sessions, and routes.
- `database.py` creates, initializes, connects to, and queries SQLite.
- `schema.sql` defines the `users` and `documents` tables.
- `templates/base.html` provides the shared header, navigation, and messages.
- `templates/home.html` defines the public home page.
- `templates/login.html` defines the login form.
- `templates/dashboard.html` loops over and displays the current student's
  document rows.
- `static/style.css` controls the page's appearance.

## Leave the virtual environment

```bash
deactivate
```

The `.venv` directory is intentionally excluded from Git and shared project
archives. Each developer creates it locally using the commands above.
