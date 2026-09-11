"""Koneksi SQLite dan migrasi skema."""

from __future__ import annotations

import sqlite3
from pathlib import Path

_SCHEMA_VERSION = 3

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
CREATE TABLE IF NOT EXISTS projects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    description TEXT    NOT NULL DEFAULT '',
    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    updated_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now'))
);

CREATE TABLE IF NOT EXISTS prompts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    content     TEXT    NOT NULL DEFAULT '',
    tool        TEXT    NOT NULL DEFAULT '',
    tags        TEXT    NOT NULL DEFAULT '[]',
    is_favorite INTEGER NOT NULL DEFAULT 0,
    project_id  INTEGER DEFAULT NULL,
    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    updated_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS commands (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    title         TEXT    NOT NULL,
    command_text  TEXT    NOT NULL DEFAULT '',
    description   TEXT    NOT NULL DEFAULT '',
    tags          TEXT    NOT NULL DEFAULT '[]',
    project_id    INTEGER DEFAULT NULL,
    created_at    TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    updated_at    TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS api_refs (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name      TEXT    NOT NULL,
    base_url          TEXT    NOT NULL DEFAULT '',
    description       TEXT    NOT NULL DEFAULT '',
    auth_type         TEXT    NOT NULL DEFAULT '',
    keychain_key_name TEXT    NOT NULL DEFAULT '',
    tags              TEXT    NOT NULL DEFAULT '[]',
    project_id        INTEGER DEFAULT NULL,
    created_at        TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    updated_at        TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
"""

_MIGRATION_V2 = """\
ALTER TABLE notes ADD COLUMN content TEXT NOT NULL DEFAULT '';
"""

_MIGRATION_V3 = """\
-- Tambahkan project_id ke tabel yang sudah ada jika belum ada
ALTER TABLE prompts ADD COLUMN project_id INTEGER DEFAULT NULL;
ALTER TABLE commands ADD COLUMN project_id INTEGER DEFAULT NULL;
ALTER TABLE api_refs ADD COLUMN project_id INTEGER DEFAULT NULL;
"""


def run_migrations(conn: sqlite3.Connection) -> None:
    (current_version,) = conn.execute("PRAGMA user_version").fetchone()

    if current_version < 1:
        conn.executescript(_MIGRATION_V1)
        conn.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")
        conn.commit()
    elif current_version < 2:
        conn.executescript(_MIGRATION_V2)
        conn.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")
        conn.commit()
    elif current_version < 3:
        try:
            conn.executescript(_MIGRATION_V3)
        except sqlite3.OperationalError:
            pass
        conn.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")
        conn.commit()


def init_db(db_path: Path | None = None) -> sqlite3.Connection:
    conn = get_connection(db_path)
    run_migrations(conn)
    return conn
