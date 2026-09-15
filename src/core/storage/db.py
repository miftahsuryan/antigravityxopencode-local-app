"""Koneksi SQLite dan migrasi skema."""

from __future__ import annotations

import sqlite3
from pathlib import Path

_SCHEMA_VERSION = 2

_APP_SUPPORT_DIR = Path.home() / "Library" / "Application Support" / "DevCodex"


def _default_db_path() -> Path:
    _APP_SUPPORT_DIR.mkdir(parents=True, exist_ok=True)
    return _APP_SUPPORT_DIR / "devcodex.db"


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or _default_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


_MIGRATION_V1 = """\
CREATE TABLE IF NOT EXISTS labels (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    color       TEXT    NOT NULL DEFAULT '#6C8CFF',
    description TEXT    NOT NULL DEFAULT '',
    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    updated_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now'))
);

CREATE TABLE IF NOT EXISTS prompts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    content     TEXT    NOT NULL DEFAULT '',
    tool        TEXT    NOT NULL DEFAULT '',
    is_favorite INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    updated_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now'))
);

CREATE TABLE IF NOT EXISTS commands (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    title         TEXT    NOT NULL,
    command_text  TEXT    NOT NULL DEFAULT '',
    description   TEXT    NOT NULL DEFAULT '',
    created_at    TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    updated_at    TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now'))
);

CREATE TABLE IF NOT EXISTS api_refs (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name      TEXT    NOT NULL,
    base_url          TEXT    NOT NULL DEFAULT '',
    description       TEXT    NOT NULL DEFAULT '',
    auth_type         TEXT    NOT NULL DEFAULT '',
    keychain_key_name TEXT    NOT NULL DEFAULT '',
    created_at        TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    updated_at        TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now'))
);

CREATE TABLE IF NOT EXISTS label_items (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    label_id  INTEGER NOT NULL,
    item_type TEXT    NOT NULL,
    item_id   INTEGER NOT NULL,
    FOREIGN KEY (label_id) REFERENCES labels(id) ON DELETE CASCADE,
    UNIQUE(label_id, item_type, item_id)
);
"""


_MIGRATION_V2 = """\
CREATE TABLE IF NOT EXISTS doc_folders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    parent_id   INTEGER DEFAULT NULL,
    color       TEXT    NOT NULL DEFAULT '#6C8CFF',
    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    updated_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    FOREIGN KEY (parent_id) REFERENCES doc_folders(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS doc_files (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    content     TEXT    NOT NULL DEFAULT '',
    folder_id   INTEGER DEFAULT NULL,
    file_type   TEXT    NOT NULL DEFAULT 'md',
    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    updated_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    FOREIGN KEY (folder_id) REFERENCES doc_folders(id) ON DELETE CASCADE
);
"""


def run_migrations(conn: sqlite3.Connection) -> None:
    (current_version,) = conn.execute("PRAGMA user_version").fetchone()

    if current_version < 1:
        conn.executescript(_MIGRATION_V1)
        conn.execute("PRAGMA user_version = 1")
        conn.commit()

    if current_version < 2:
        conn.executescript(_MIGRATION_V2)
        conn.execute("PRAGMA user_version = 2")
        conn.commit()


def init_db(db_path: Path | None = None) -> sqlite3.Connection:
    conn = get_connection(db_path)
    run_migrations(conn)
    return conn
