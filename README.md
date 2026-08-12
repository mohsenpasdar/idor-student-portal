# IDOR Student Document Portal

An educational Flask project that will demonstrate and prevent insecure direct
object reference (IDOR) vulnerabilities using fictional student data.

> This project is for a controlled local security demonstration. It must not be
> deployed publicly or used with real personal information.

## Current milestone

Phase 3.1 is complete. The application keeps the intentionally vulnerable IDOR
route for comparison and adds the first server-side defense: retrieve the
document, verify that its owner ID matches the signed-in user's ID, and return
`403 Forbidden` when the ownership check fails.

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

## Test the dashboard, vulnerable route, and ownership check

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

To demonstrate the intentional vulnerability:

1. Log in as Alice.
2. Open document `1` from Alice's dashboard.
3. Confirm that the browser address ends with
   `/document/vulnerable/1`.
4. Change only the final `1` to `3` and press Enter.
5. Bob's grade report is displayed even though Alice is still signed in.

Both requests return `200 OK`. The second result is the planned security
failure: authentication is enforced, but document ownership is not.

Opening a vulnerable document URL while logged out redirects to `/login`, and
requesting a document ID that does not exist returns a styled `404 Not Found`
page while preserving the correct HTTP status code.

To test the Phase 3.1 ownership-check defense:

1. Stay logged in as Alice.
2. Open document `1` using **Ownership check** on the dashboard.
3. Confirm that the browser address ends with
   `/document/ownership-check/1` and the document is displayed.
4. Change only the final `1` to Bob's document ID `3` and press Enter.
5. Confirm that Flask returns the styled `403 Forbidden` page and does not
   display Bob's document content.

The route first retrieves the requested document and then compares its
`owner_id` with `g.user["id"]`. Alice's own document returns `200 OK`, while
Bob's document returns `403 Forbidden`. The `403` response confirms that the
document exists, but its private content is not disclosed.

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

## Authentication, dashboard filtering, and IDOR

- `load_logged_in_user()` reads `user_id` from the signed session and loads the
  matching database user into Flask's request-local `g` object.
- `login_required` protects routes that should only be available to an
  authenticated student.
- `/login` verifies the submitted credentials and creates the session.
- `/logout` clears the session and returns to the public home page.
- `/dashboard` passes `g.user["id"]` to `get_documents_by_owner()` and sends the
  resulting rows to `dashboard.html`.
- `dashboard.html` loops over those rows and displays each document's type,
  title, numeric ID, and a link to the individual document page.
- `/document/vulnerable/<document_id>` requires login but retrieves a document
  using only the numeric ID from the URL.
- `/document/ownership-check/<document_id>` requires login, retrieves the
  document, and returns `403 Forbidden` unless its `owner_id` matches the
  signed-in user's ID.
- `document.html` displays the selected document's owner, metadata, and full
  fictional content after the selected route permits access.

The dashboard query includes `owner_id`, so one student's list cannot contain
another student's documents. Authentication answers **who the user is**, while
this owner-filtered query controls which records appear in the dashboard.

The dashboard query is safe because it includes the signed-in student's owner
ID. The individual vulnerable route is not safe because it never compares
`document["owner_id"]` with `g.user["id"]`. A logged-in student can therefore
change the numeric URL value and retrieve another student's document. This is
the controlled IDOR baseline defined in the approved experiment scope.

The page clearly labels this behaviour because the application is an
educational local prototype. Phase 3.1 adds the ownership-check defense as a
separate route, while the user-scoped-query defense remains for Phase 3.2.

## Files used through Phase 3.1

- `app.py` creates Flask and handles authentication, sessions, and routes.
- `database.py` creates, initializes, connects to, and queries SQLite.
- `schema.sql` defines the `users` and `documents` tables.
- `templates/base.html` provides the shared header, navigation, and messages.
- `templates/home.html` defines the public home page.
- `templates/login.html` defines the login form.
- `templates/dashboard.html` loops over and displays the current student's
  document rows and links to both the vulnerable and ownership-check routes.
- `templates/document.html` labels the selected implementation and displays a
  document only after the route permits access.
- `templates/error.html` provides a shared page for expected `403 Forbidden`
  and `404 Not Found` responses.
- `static/style.css` controls the page's appearance.

## Phase 2 completion checklist

- Logged-out access to `/dashboard` redirects to `/login`.
- Alice can log in and sees only document IDs `1` and `2`.
- Alice can open her own document `1`.
- Changing the vulnerable URL from document `1` to Bob's document `3` exposes
  Bob's fictional grade report with `200 OK`, confirming the planned IDOR.
- A nonexistent document such as `999` returns the styled `404` page.
- Bob and Charlie each see only their own two documents.
- Logging out clears the session and protects the dashboard again.

## Phase 3.1 validation checklist

- Logged-out access to the ownership-check route redirects to `/login`.
- Alice can access her own document `1` through the ownership-check route with
  `200 OK`.
- Alice cannot access Bob's document `3` through the ownership-check route;
  Flask returns `403 Forbidden` without displaying Bob's private content.
- A nonexistent document such as `999` returns `404 Not Found`.
- Bob can access his own document `3` through the ownership-check route with
  `200 OK`.
- The vulnerable route remains unchanged and still returns Bob's document `3`
  to Alice with `200 OK`, preserving the experiment's baseline.

## Leave the virtual environment

```bash
deactivate
```

The `.venv` directory is intentionally excluded from Git and shared project
archives. Each developer creates it locally using the commands above.
