# IDOR Student Document Portal

An educational Flask and SQLite application that demonstrates an insecure
direct object reference (IDOR) vulnerability and compares two server-side
authorization defenses.

The portal uses only fictional students, credentials, and documents. It is
intended for a controlled local security experiment.

> **Security warning:** This application intentionally contains a vulnerable
> endpoint. Run it only on your own computer. Do not deploy it publicly or use
> real personal information.

## Project objective

The project demonstrates that authentication alone does not protect individual
objects. A student can be correctly logged in but still access another
student's private document when the server trusts a document ID without
checking ownership.

The application compares three implementations:

| Implementation | Route | Cross-user result |
| --- | --- | --- |
| Vulnerable baseline | `/document/vulnerable/<document_id>` | `200 OK`; private data exposed |
| Ownership-check defense | `/document/ownership-check/<document_id>` | `403 Forbidden`; access blocked |
| User-scoped-query defense | `/document/scoped-query/<document_id>` | `404 Not Found`; unauthorized row not returned |

## Main features

- Flask web application with server-rendered HTML pages
- SQLite database with three fictional users and six fictional documents
- Password hashing with Werkzeug
- Signed session-based login and logout
- Dashboard filtered to the signed-in student's documents
- Intentionally vulnerable IDOR endpoint
- Ownership-check authorization defense
- User-scoped database-query defense
- Shared `403 Forbidden` and `404 Not Found` pages

## Requirements

- Git, if cloning the repository
- Python 3.10 or newer
- `pip`, normally included with Python

SQLite support is included with Python. No separate database server or SQLite
installation is required.

## Download the project

Clone the repository and enter its directory:

```bash
git clone <repository-url>
cd idor-student-portal
```

Replace `<repository-url>` with the HTTPS or SSH URL shown on the project's
GitHub page. If the project was downloaded as a ZIP file instead, extract it
and open a terminal inside the extracted `idor-student-portal` directory.

## Set up the project

Using a virtual environment keeps this project's packages separate from other
Python projects.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If Windows does not recognize `python`, try `py` in the first and third
commands. If PowerShell blocks the activation script, run this once in the
current terminal and then activate the environment again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Windows Command Prompt

```bat
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

After activation, the terminal prompt normally begins with `(.venv)`.

## Initialize the fictional database

With the virtual environment active, run:

```bash
python database.py
```

Expected output:

```text
Database initialized: .../instance/portal.db
Users: 3
Documents: 6
```

This creates `instance/portal.db` and loads the fictional records. Running the
command again resets the database to the same starting data.

## Run the application

Start the local Flask development server:

```bash
python app.py
```

Open this address in a browser:

```text
http://127.0.0.1:5000
```

Keep the terminal open while using the portal. Press `Ctrl+C` in the terminal
to stop the server.

## Fictional accounts

Open `http://127.0.0.1:5000/login` and use one of these accounts:

| Name | Username | Password | Document IDs |
| --- | --- | --- | --- |
| Alice Johnson | `alice` | `alice123` | `1`, `2` |
| Bob Smith | `bob` | `bob123` | `3`, `4` |
| Charlie Brown | `charlie` | `charlie123` | `5`, `6` |

These passwords are intentionally simple demo credentials. The database stores
password hashes rather than the plain-text passwords.

## Reproduce the IDOR experiment

Use the same signed-in user and target document for all three routes.

### 1. Confirm normal access

1. Log in as Alice.
2. Confirm that Alice's dashboard lists only documents `1` and `2`.
3. Open Alice's document `1` through each route.

All three routes should display Alice's document with `200 OK`.

### 2. Demonstrate the vulnerability

1. While still logged in as Alice, open:

   ```text
   http://127.0.0.1:5000/document/vulnerable/1
   ```

2. Change only the final document ID from `1` to Bob's document ID `3`:

   ```text
   http://127.0.0.1:5000/document/vulnerable/3
   ```

3. The server returns `200 OK` and displays Bob Smith's fictional grade report.

Alice is authenticated, but the route retrieves the document using only the
browser-controlled ID. It never checks whether Alice owns the document.

### 3. Test the ownership-check defense

While still logged in as Alice, open:

```text
http://127.0.0.1:5000/document/ownership-check/3
```

The application retrieves document `3`, compares its `owner_id` with Alice's
user ID, and returns `403 Forbidden`. Bob's private content is not displayed.

### 4. Test the user-scoped-query defense

While still logged in as Alice, open:

```text
http://127.0.0.1:5000/document/scoped-query/3
```

The database searches using both document ID `3` and Alice's user ID. No row
matches, so the application returns `404 Not Found`. Bob's document is not
returned to the Flask route.

### 5. Confirm legitimate access is preserved

Log out, sign in as Bob, and open document `3` through both secure routes. Both
requests should return `200 OK` because Bob is the document owner.

## Manual experiment results

| Request | Vulnerable route | Ownership check | Scoped query |
| --- | --- | --- | --- |
| Alice requests her document `1` | `200` | `200` | `200` |
| Alice requests Bob's document `3` | `200`; exposed | `403`; blocked | `404`; hidden |
| Bob requests his document `3` | `200` | `200` | `200` |
| Alice requests nonexistent document `999` | `404` | `404` | `404` |

The vulnerable route retrieves and displays Bob's row. The ownership-check
route retrieves the row and rejects Alice afterward. The scoped-query route
includes the authenticated user ID in SQL, so Bob's row is not returned.

The `404` response can reveal less information than `403`, but the status code
is not the security control by itself. The protection comes from enforcing
object-level authorization on the server.

## Project structure

```text
idor-student-portal/
|-- app.py
|-- database.py
|-- schema.sql
|-- requirements.txt
|-- README.md
|-- instance/
|   `-- .gitkeep
|-- static/
|   `-- style.css
`-- templates/
    |-- base.html
    |-- dashboard.html
    |-- document.html
    |-- error.html
    |-- home.html
    `-- login.html
```

- `app.py` configures Flask, authentication, sessions, routes, and errors.
- `database.py` initializes SQLite and contains reusable parameterized queries.
- `schema.sql` defines the `users` and `documents` tables.
- `templates/` contains the Jinja HTML templates.
- `static/style.css` contains the application styling.
- `instance/portal.db` is generated locally and is excluded from Git.

## Security design notes

- The dashboard query is filtered by the authenticated user's ID.
- All SQL queries use placeholders instead of building SQL from user input.
- The session cookie stores only the user's numeric ID, not a password or hash.
- The cookie is marked `HttpOnly` and `SameSite=Lax`.
- If `PORTAL_SECRET_KEY` is not set, the app generates a temporary random
  signing key. Existing sessions therefore end when the server restarts.
- The `Secure` cookie setting is not enabled because the controlled local demo
  uses HTTP instead of HTTPS.

For this local experiment, no secret-key setup is required. A custom key can be
provided before starting the application if needed:

```powershell
$env:PORTAL_SECRET_KEY = "replace-with-a-random-development-key"
python app.py
```

On macOS or Linux:

```bash
export PORTAL_SECRET_KEY="replace-with-a-random-development-key"
python app.py
```

## Limitations

- This is a simplified educational prototype, not a production portal.
- All users, credentials, and documents are fictional.
- Numeric IDs make guessing easy, but replacing them with UUIDs would not fix
  missing authorization.
- Both defenses are valid in this small application; the scoped query is the
  preferred design because unauthorized rows are not returned to the route.
- The project does not evaluate password policy, CSRF, XSS, SQL injection,
  logging, rate limiting, or production deployment security.
- A real student portal would require stronger authentication, centralized
  authorization, HTTPS, secure configuration, audit logging, and broader tests.

## Troubleshooting

- **`ModuleNotFoundError: No module named 'flask'`:** Activate `.venv` and run
  `python -m pip install -r requirements.txt` again.
- **`no such table: users`:** Run `python database.py` before starting the app.
- **Port 5000 is already in use:** Stop the other Flask process with `Ctrl+C`,
  then run `python app.py` again.
- **Old page or styling appears:** Refresh with `Ctrl+F5` to bypass the browser
  cache.

## Leave the virtual environment

After stopping the server, run:

```bash
deactivate
```

The `.venv` directory and generated `instance/portal.db` are intentionally
excluded from Git. Each user recreates them locally using the instructions
above.
