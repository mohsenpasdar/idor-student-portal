"""Create and initialize the fictional SQLite database."""

from pathlib import Path
import sqlite3

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


def connect_database():
    """Open the project database and enable foreign-key enforcement."""
    INSTANCE_DIRECTORY.mkdir(exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


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
