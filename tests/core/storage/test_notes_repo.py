"""Test CRUD notes_repo."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.core.models import Note
from src.core.storage.db import init_db
from src.core.storage.notes_repo import (
    create_note,
    delete_note,
    get_note,
    list_notes,
    update_note,
)


@pytest.fixture()
def conn(tmp_path: Path) -> sqlite3.Connection:
    return init_db(tmp_path / "test.db")


def test_create_and_get(conn: sqlite3.Connection) -> None:
    note = Note(id=None, title="Hello", file_path="notes/hello.md")
    saved = create_note(conn, note)
    assert saved.id is not None
    assert saved.title == "Hello"

    fetched = get_note(conn, saved.id)
    assert fetched is not None
    assert fetched.title == "Hello"


def test_list_notes(conn: sqlite3.Connection) -> None:
    create_note(conn, Note(id=None, title="A", file_path="notes/a.md"))
    create_note(conn, Note(id=None, title="B", file_path="notes/b.md"))
    notes = list_notes(conn)
    assert len(notes) == 2


def test_update_note(conn: sqlite3.Connection) -> None:
    saved = create_note(conn, Note(id=None, title="Old", file_path="notes/old.md"))
    saved.title = "New"
    updated = update_note(conn, saved)
    assert updated is not None
    assert updated.title == "New"


def test_delete_note(conn: sqlite3.Connection) -> None:
    saved = create_note(conn, Note(id=None, title="Bye", file_path="notes/bye.md"))
    assert delete_note(conn, saved.id) is True  # type: ignore[arg-type]
    assert get_note(conn, saved.id) is None  # type: ignore[arg-type]


def test_delete_nonexistent(conn: sqlite3.Connection) -> None:
    assert delete_note(conn, 9999) is False


def test_tags_roundtrip(conn: sqlite3.Connection) -> None:
    note = Note(
        id=None,
        title="Tagged",
        file_path="notes/tagged.md",
        tags=["python", "flet"],
    )
    saved = create_note(conn, note)
    fetched = get_note(conn, saved.id)  # type: ignore[arg-type]
    assert fetched is not None
    assert fetched.tags == ["python", "flet"]
