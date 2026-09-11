"""Test CRUD commands_repo."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.core.models import Command
from src.core.storage.commands_repo import (
    create_command,
    delete_command,
    get_command,
    list_commands,
    update_command,
)
from src.core.storage.db import init_db


@pytest.fixture()
def conn(tmp_path: Path) -> sqlite3.Connection:
    return init_db(tmp_path / "test.db")


def test_create_and_get(conn: sqlite3.Connection) -> None:
    cmd = Command(
        id=None,
        title="Docker PS",
        command_text="docker ps -a",
        description="List all containers",
    )
    saved = create_command(conn, cmd)
    assert saved.id is not None
    assert saved.command_text == "docker ps -a"

    fetched = get_command(conn, saved.id)
    assert fetched is not None
    assert fetched.command_text == "docker ps -a"


def test_list_commands(conn: sqlite3.Connection) -> None:
    create_command(conn, Command(id=None, title="A", command_text="ls"))
    create_command(conn, Command(id=None, title="B", command_text="pwd"))
    assert len(list_commands(conn)) == 2


def test_update_command(conn: sqlite3.Connection) -> None:
    saved = create_command(conn, Command(id=None, title="Old", command_text="echo old"))
    saved.command_text = "echo new"
    updated = update_command(conn, saved)
    assert updated is not None
    assert updated.command_text == "echo new"


def test_delete_command(conn: sqlite3.Connection) -> None:
    saved = create_command(conn, Command(id=None, title="Bye", command_text="exit"))
    assert delete_command(conn, saved.id) is True  # type: ignore[arg-type]
    assert get_command(conn, saved.id) is None  # type: ignore[arg-type]
