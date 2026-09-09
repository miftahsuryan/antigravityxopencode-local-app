"""Test CRUD api_refs_repo."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.core.models import ApiRef
from src.core.storage.api_refs_repo import (
    create_api_ref,
    delete_api_ref,
    get_api_ref,
    list_api_refs,
    update_api_ref,
)
from src.core.storage.db import init_db


@pytest.fixture()
def conn(tmp_path: Path) -> sqlite3.Connection:
    return init_db(tmp_path / "test.db")


def test_create_and_get(conn: sqlite3.Connection) -> None:
    ref = ApiRef(
        id=None,
        service_name="GitHub API",
        base_url="https://api.github.com",
        description="GitHub REST API",
        auth_type="Bearer",
        keychain_key_name="github-token",
        tags=["github"],
    )
    saved = create_api_ref(conn, ref)
    assert saved.id is not None
    assert saved.service_name == "GitHub API"

    fetched = get_api_ref(conn, saved.id)
    assert fetched is not None
    assert fetched.keychain_key_name == "github-token"


def test_list_api_refs(conn: sqlite3.Connection) -> None:
    create_api_ref(conn, ApiRef(id=None, service_name="A", base_url="https://a.com"))
    create_api_ref(conn, ApiRef(id=None, service_name="B", base_url="https://b.com"))
    assert len(list_api_refs(conn)) == 2


def test_update_api_ref(conn: sqlite3.Connection) -> None:
    saved = create_api_ref(
        conn,
        ApiRef(id=None, service_name="Old", base_url="https://old.com"),
    )
    saved.base_url = "https://new.com"
    updated = update_api_ref(conn, saved)
    assert updated is not None
    assert updated.base_url == "https://new.com"


def test_delete_api_ref(conn: sqlite3.Connection) -> None:
    saved = create_api_ref(
        conn, ApiRef(id=None, service_name="Bye", base_url="https://bye.com")
    )
    assert delete_api_ref(conn, saved.id) is True  # type: ignore[arg-type]
    assert get_api_ref(conn, saved.id) is None  # type: ignore[arg-type]
