"""Create, initialize, and query the fictional SQLite database."""

from pathlib import Path
import sqlite3

from flask import current_app, g
from werkzeug.security import generate_password_hash


PROJECT_ROOT = Path(__file__).resolve().parent
INSTANCE_DIRECTORY = PROJECT_ROOT / "instance"
DATABASE_PATH = INSTANCE_DIRECTORY / "portal.db"
SCHEMA_PATH = PROJECT_ROOT / "schema.sql"


USERS = (
    (1, "Alice Johnson", "alice", "alice123"),
    (2, "Bob Smith", "bob", "bob123"),
    (3, "Charlie Brown", "charlie", "charlie123"),
)

DOCUMENTS = (
    (
        1,
        1,
        "Fall 2026 Grade Report",
        "Grade Report",
        "Course: Fundamentals of Security\nFinal grade: A",
    ),
    (
        2,
        1,
        "2026 Enrollment Letter",
        "Enrollment Letter",
        "Enrollment status: Full-time",
    ),
    (
        3,
        2,
        "Fall 2026 Grade Report",
        "Grade Report",
        "Course: Fundamentals of Security\nFinal grade: B+",
    ),
    (
        4,
        2,
        "Fall 2026 Tuition Statement",
        "Tuition Statement",
        "Amount due: $4,250",
    ),
    (
        5,
        3,
        "Fall 2026 Grade Report",
        "Grade Report",
        "Course: Fundamentals of Security\nFinal grade: A-",
    ),
    (
        6,
        3,
        "2026 Enrollment Letter",
        "Enrollment Letter",
        "Enrollment status: Part-time",
    ),
)


def connect_database(database_path=DATABASE_PATH):
    """Open the project database and enable foreign-key enforcement."""
    INSTANCE_DIRECTORY.mkdir(exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_database():
    """Return one database connection for the current Flask request."""
    if "database" not in g:
        g.database = connect_database(current_app.config["DATABASE"])

    return g.database


def close_database(_exception=None):
    """Close the current request's database connection, if one exists."""
    database = g.pop("database", None)

    if database is not None:
        database.close()


def init_app(app):
    """Configure database access for a Flask application."""
    app.config.setdefault("DATABASE", DATABASE_PATH)
    app.teardown_appcontext(close_database)


def get_user_by_id(user_id):
    """Return one user by primary key, or None when the user does not exist."""
    return get_database().execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()


def get_user_by_username(username):
    """Return one user by username, or None when the user does not exist."""
    return get_database().execute(
        "SELECT * FROM users WHERE username = ?",
        (username,),
    ).fetchone()


def get_documents_by_owner(owner_id):
    """Return all documents owned by one user in document-ID order."""
    return get_database().execute(
        "SELECT * FROM documents WHERE owner_id = ? ORDER BY id",
        (owner_id,),
    ).fetchall()


def get_document_by_id(document_id):
    """Return one document by primary key, or None when it does not exist."""
    return get_database().execute(
        "SELECT * FROM documents WHERE id = ?",
        (document_id,),
    ).fetchone()


def initialize_database():
    """Recreate the schema and load the approved fictional records."""
    database = connect_database()

    try:
        database.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

        database.executemany(
            """
            INSERT INTO users (id, name, username, password_hash)
            VALUES (?, ?, ?, ?)
            """,
            (
                (user_id, name, username, generate_password_hash(password))
                for user_id, name, username, password in USERS
            ),
        )

        database.executemany(
            """
            INSERT INTO documents (id, owner_id, title, document_type, content)
            VALUES (?, ?, ?, ?, ?)
            """,
            DOCUMENTS,
        )
        database.commit()

        user_count = database.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        document_count = database.execute(
            "SELECT COUNT(*) FROM documents"
        ).fetchone()[0]
    finally:
        database.close()

    return user_count, document_count


if __name__ == "__main__":
    users_created, documents_created = initialize_database()
    print(f"Database initialized: {DATABASE_PATH}")
    print(f"Users: {users_created}")
    print(f"Documents: {documents_created}")
