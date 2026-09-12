"""Test search_all: global search across all modules."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.core.models import ApiRef, Command, Label, Prompt
from src.core.search import search_all
from src.core.storage import api_refs_repo, commands_repo, labels_repo, prompts_repo
from src.core.storage.db import init_db


@pytest.fixture()
def conn(tmp_path: Path) -> sqlite3.Connection:
    return init_db(tmp_path / "test.db")


def _seed_data(conn: sqlite3.Connection) -> None:
    """Insert sample data for search testing."""
    labels_repo.create_label(conn, Label(id=None, name="Backend"))
    labels_repo.create_label(conn, Label(id=None, name="Frontend"))

    prompts_repo.create_prompt(
        conn,
        Prompt(
            id=None,
            title="Code Review Prompt",
            content="Review this Python code for bugs",
            tool="claude",
        ),
    )
    prompts_repo.create_prompt(
        conn,
        Prompt(id=None, title="Design System", content="Create a UI design system"),
    )

    commands_repo.create_command(
        conn,
        Command(
            id=None,
            title="Docker Compose Up",
            command_text="docker compose up -d",
            description="Start all containers",
        ),
    )

    api_refs_repo.create_api_ref(
        conn,
        ApiRef(
            id=None,
            service_name="OpenAI API",
            base_url="https://api.openai.com/v1",
            auth_type="Bearer Token",
        ),
    )


def test_search_finds_prompts(conn: sqlite3.Connection) -> None:
    _seed_data(conn)
    results = search_all(conn, "Code Review")
    assert len(results) >= 1
    assert any(r.module == "prompts" for r in results)


def test_search_finds_commands(conn: sqlite3.Connection) -> None:
    _seed_data(conn)
    results = search_all(conn, "docker compose")
    assert len(results) >= 1
    assert any(r.module == "commands" for r in results)


def test_search_finds_api_refs(conn: sqlite3.Connection) -> None:
    _seed_data(conn)
    results = search_all(conn, "OpenAI")
    assert len(results) >= 1
    assert any(r.module == "api_refs" for r in results)


def test_search_finds_labels(conn: sqlite3.Connection) -> None:
    _seed_data(conn)
    results = search_all(conn, "Backend")
    assert len(results) >= 1
    assert any(r.module == "labels" for r in results)


def test_search_empty_query(conn: sqlite3.Connection) -> None:
    _seed_data(conn)
    results = search_all(conn, "")
    assert results == []


def test_search_no_results(conn: sqlite3.Connection) -> None:
    _seed_data(conn)
    results = search_all(conn, "zzz_nonexistent_zzz")
    assert results == []


def test_search_cross_module(conn: sqlite3.Connection) -> None:
    _seed_data(conn)
    # "code" should match prompts (Code Review Prompt) and potentially others
    results = search_all(conn, "code")
    modules = {r.module for r in results}
    assert "prompts" in modules
