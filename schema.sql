-- Recreate the tables so the fictional demo data can be reset at any time.
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    owner_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    document_type TEXT NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES users (id)
);

CREATE INDEX idx_documents_owner_id ON documents (owner_id);
