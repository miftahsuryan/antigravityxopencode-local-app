"""Koneksi SQLite dan migrasi skema."""

from __future__ import annotations

import sqlite3
from pathlib import Path

_SCHEMA_VERSION = 4

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
ALTER TABLE notes ADD COLUMN content TEXT NOT NULL DEFAULT '';
"""

_MIGRATION_V3 = """\
ALTER TABLE prompts ADD COLUMN project_id INTEGER DEFAULT NULL;
ALTER TABLE commands ADD COLUMN project_id INTEGER DEFAULT NULL;
ALTER TABLE api_refs ADD COLUMN project_id INTEGER DEFAULT NULL;
"""

_MIGRATION_V4 = """\
CREATE TABLE IF NOT EXISTS labels (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    color       TEXT    NOT NULL DEFAULT '#6C8CFF',
    description TEXT    NOT NULL DEFAULT '',
    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    updated_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now'))
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


def run_migrations(conn: sqlite3.Connection) -> None:
    (current_version,) = conn.execute("PRAGMA user_version").fetchone()

    if current_version < 1:
        conn.executescript(_MIGRATION_V1)
        conn.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")
        conn.commit()
    elif current_version < 2:
        try:
            conn.executescript(_MIGRATION_V2)
        except sqlite3.OperationalError:
            pass
        conn.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")
        conn.commit()
    elif current_version < 3:
        try:
            conn.executescript(_MIGRATION_V3)
        except sqlite3.OperationalError:
            pass
        conn.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")
        conn.commit()
    elif current_version < 4:
        try:
            conn.executescript(_MIGRATION_V4)
        except sqlite3.OperationalError:
            pass
        conn.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")
        conn.commit()


def init_db(db_path: Path | None = None) -> sqlite3.Connection:
    conn = get_connection(db_path)
    run_migrations(conn)
    return conn
