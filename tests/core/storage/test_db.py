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
    """Tabel utama harus ada setelah init_db."""
    tables = {
        row[0]
        for row in tmp_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    assert "labels" in tables
    assert "label_items" in tables
    assert "prompts" in tables
    assert "commands" in tables
    assert "api_refs" in tables


def test_user_version_is_set(tmp_db: sqlite3.Connection) -> None:
    """PRAGMA user_version harus 4 setelah migrasi."""
    (version,) = tmp_db.execute("PRAGMA user_version").fetchone()
    assert version == 4


def test_migration_idempotent(tmp_path: Path) -> None:
    """Menjalankan migrasi dua kali tidak boleh error."""
    conn = init_db(tmp_path / "test.db")
    run_migrations(conn)
    (version,) = conn.execute("PRAGMA user_version").fetchone()
    assert version == 4
    conn.close()


def test_labels_table_has_correct_columns(tmp_db: sqlite3.Connection) -> None:
    """Tabel labels harus memiliki kolom name, color, description."""
    columns = {
        row[1]
        for row in tmp_db.execute(
            "PRAGMA table_info(labels)"
        ).fetchall()
    }
    assert "name" in columns
    assert "color" in columns
    assert "description" in columns


def test_label_items_junction_table(tmp_db: sqlite3.Connection) -> None:
    """Tabel label_items harus bisa menyimpan relasi."""
    tmp_db.execute(
        "INSERT INTO labels (name, color) VALUES (?, ?)",
        ("Backend", "#6C8CFF"),
    )
    tmp_db.execute(
        "INSERT INTO prompts (title, content) VALUES (?, ?)",
        ("Test Prompt", "Hello"),
    )
    tmp_db.execute(
        "INSERT INTO label_items (label_id, item_type, item_id) VALUES (?, ?, ?)",
        (1, "prompts", 1),
    )
    row = tmp_db.execute(
        "SELECT * FROM label_items WHERE label_id = 1"
    ).fetchone()
    assert row is not None
    assert row["item_type"] == "prompts"
    assert row["item_id"] == 1


def test_label_unique_constraint(tmp_db: sqlite3.Connection) -> None:
    """Nama label harus unik."""
    tmp_db.execute(
        "INSERT INTO labels (name, color) VALUES (?, ?)",
        ("Backend", "#6C8CFF"),
    )
    with pytest.raises(sqlite3.IntegrityError):
        tmp_db.execute(
            "INSERT INTO labels (name, color) VALUES (?, ?)",
            ("Backend", "#FF0000"),
        )
