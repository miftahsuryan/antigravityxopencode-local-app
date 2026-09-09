"""Test db.py: koneksi dan migrasi skema."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.core.storage.db import init_db, run_migrations


@pytest.fixture()
def tmp_db(tmp_path: Path) -> sqlite3.Connection:
    """Fixture: DB in-memory-like tapi di temp directory."""
    return init_db(tmp_path / "test.db")


def test_init_db_creates_tables(tmp_db: sqlite3.Connection) -> None:
    """Keempat tabel harus ada setelah init_db."""
    tables = {
        row[0]
        for row in tmp_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    assert "notes" in tables
    assert "prompts" in tables
    assert "commands" in tables
    assert "api_refs" in tables


def test_user_version_is_set(tmp_db: sqlite3.Connection) -> None:
    """PRAGMA user_version harus 1 setelah migrasi."""
    (version,) = tmp_db.execute("PRAGMA user_version").fetchone()
    assert version == 1


def test_migration_idempotent(tmp_path: Path) -> None:
    """Menjalankan migrasi dua kali tidak boleh error."""
    conn = init_db(tmp_path / "test.db")
    run_migrations(conn)  # second run — should be no-op
    (version,) = conn.execute("PRAGMA user_version").fetchone()
    assert version == 1
    conn.close()
