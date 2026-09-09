"""Koneksi SQLite dan migrasi skema.

Menggunakan ``PRAGMA user_version`` untuk tracking versi migrasi.
Semua tabel dibuat di sini; lihat docs/paper-trail/0001-mvp-core-modules.md.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

# Versi skema saat ini — naikkan setiap kali ada perubahan DDL.
_SCHEMA_VERSION = 1

# Lokasi DB mengikuti konvensi macOS: ~/Library/Application Support/DevCodex/.
# Sesuai .agents/rules/security-and-data.md — data pribadi TIDAK disimpan di
# dalam folder repo Git; folder data/ di repo hanya untuk sample dev.
_APP_SUPPORT_DIR = Path.home() / "Library" / "Application Support" / "DevCodex"


def _default_db_path() -> Path:
    """Tentukan path DB di Application Support macOS.

    Returns:
        Path absolut ke file database.
    """
    _APP_SUPPORT_DIR.mkdir(parents=True, exist_ok=True)
    return _APP_SUPPORT_DIR / "devcodex.db"


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Buat atau ambil koneksi ke SQLite.

    Args:
        db_path: path opsional ke file DB.  Kalau None, pakai default.

    Returns:
        Koneksi SQLite dengan row_factory = sqlite3.Row.
    """
    path = db_path or _default_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ---------------------------------------------------------------------------
# Migrasi
# ---------------------------------------------------------------------------

_MIGRATION_V1 = """\
CREATE TABLE IF NOT EXISTS notes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    file_path   TEXT    NOT NULL UNIQUE,
    tags        TEXT    NOT NULL DEFAULT '[]',
    folder      TEXT    NOT NULL DEFAULT '',
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
    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    updated_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now'))
);

CREATE TABLE IF NOT EXISTS commands (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    title         TEXT    NOT NULL,
    command_text  TEXT    NOT NULL DEFAULT '',
    description   TEXT    NOT NULL DEFAULT '',
    tags          TEXT    NOT NULL DEFAULT '[]',
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
    tags              TEXT    NOT NULL DEFAULT '[]',
    created_at        TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    updated_at        TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now'))
);
"""


def run_migrations(conn: sqlite3.Connection) -> None:
    """Jalankan migrasi skema yang belum diaplikasikan.

    Args:
        conn: koneksi SQLite yang sudah terbuka.
    """
    (current_version,) = conn.execute("PRAGMA user_version").fetchone()

    if current_version < 1:
        conn.executescript(_MIGRATION_V1)
        conn.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")
        conn.commit()


def init_db(db_path: Path | None = None) -> sqlite3.Connection:
    """Helper: buat koneksi + jalankan migrasi sekaligus.

    Args:
        db_path: path opsional ke file DB.

    Returns:
        Koneksi SQLite yang sudah siap pakai.
    """
    conn = get_connection(db_path)
    run_migrations(conn)
    return conn
