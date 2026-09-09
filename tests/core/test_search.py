"""Test search global lintas modul."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.core.models import ApiRef, Command, Note, Prompt
from src.core.search import search_all
from src.core.storage.api_refs_repo import create_api_ref
from src.core.storage.commands_repo import create_command
from src.core.storage.db import init_db
from src.core.storage.notes_repo import create_note
from src.core.storage.prompts_repo import create_prompt


@pytest.fixture()
def conn(tmp_path: Path) -> sqlite3.Connection:
    db = init_db(tmp_path / "test.db")
    # Seed data
    create_note(db, Note(id=None, title="Python Tips", file_path="notes/py.md"))
    create_prompt(
        db,
        Prompt(id=None, title="Code Review", content="Review this Python code"),
    )
    create_command(
        db,
        Command(id=None, title="Git Log", command_text="git log --oneline"),
    )
    create_api_ref(
        db,
        ApiRef(
            id=None,
            service_name="Python Docs",
            base_url="https://docs.python.org",
        ),
    )
    return db


def test_search_finds_across_modules(conn: sqlite3.Connection) -> None:
    results = search_all(conn, "Python")
    modules = {r.module for r in results}
    # "Python" muncul di notes (title), prompts (content), api_refs (service_name)
    assert "notes" in modules
    assert "prompts" in modules
    assert "api_refs" in modules


def test_search_no_results(conn: sqlite3.Connection) -> None:
    results = search_all(conn, "XYZNONEXISTENT")
    assert results == []


def test_search_empty_query(conn: sqlite3.Connection) -> None:
    results = search_all(conn, "")
    assert results == []


def test_search_finds_command(conn: sqlite3.Connection) -> None:
    results = search_all(conn, "git")
    modules = {r.module for r in results}
    assert "commands" in modules
