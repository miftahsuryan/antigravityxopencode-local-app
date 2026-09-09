"""Test CRUD prompts_repo."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.core.models import Prompt
from src.core.storage.db import init_db
from src.core.storage.prompts_repo import (
    create_prompt,
    delete_prompt,
    get_prompt,
    list_prompts,
    update_prompt,
)


@pytest.fixture()
def conn(tmp_path: Path) -> sqlite3.Connection:
    return init_db(tmp_path / "test.db")


def test_create_and_get(conn: sqlite3.Connection) -> None:
    prompt = Prompt(
        id=None, title="System Prompt", content="You are helpful.", tool="claude"
    )
    saved = create_prompt(conn, prompt)
    assert saved.id is not None
    assert saved.tool == "claude"

    fetched = get_prompt(conn, saved.id)
    assert fetched is not None
    assert fetched.content == "You are helpful."


def test_list_prompts(conn: sqlite3.Connection) -> None:
    create_prompt(conn, Prompt(id=None, title="A", content="a"))
    create_prompt(conn, Prompt(id=None, title="B", content="b"))
    assert len(list_prompts(conn)) == 2


def test_update_prompt(conn: sqlite3.Connection) -> None:
    saved = create_prompt(conn, Prompt(id=None, title="Old", content="old content"))
    saved.content = "new content"
    updated = update_prompt(conn, saved)
    assert updated is not None
    assert updated.content == "new content"


def test_delete_prompt(conn: sqlite3.Connection) -> None:
    saved = create_prompt(conn, Prompt(id=None, title="Bye", content="bye"))
    assert delete_prompt(conn, saved.id) is True  # type: ignore[arg-type]
    assert get_prompt(conn, saved.id) is None  # type: ignore[arg-type]


def test_favorite_flag(conn: sqlite3.Connection) -> None:
    saved = create_prompt(
        conn,
        Prompt(id=None, title="Fav", content="fav", is_favorite=True),
    )
    fetched = get_prompt(conn, saved.id)  # type: ignore[arg-type]
    assert fetched is not None
    assert fetched.is_favorite is True
