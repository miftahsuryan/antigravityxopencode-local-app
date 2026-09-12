"""Test import/export JSON functionality."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from src.core.io import export_to_json, import_from_json
from src.core.models import ApiRef, Command, Label, Prompt
from src.core.storage import (
    api_refs_repo,
    commands_repo,
    labels_repo,
    prompts_repo,
)
from src.core.storage.db import init_db


@pytest.fixture()
def conn(tmp_path: Path) -> sqlite3.Connection:
    return init_db(tmp_path / "test.db")


def _seed_data(conn: sqlite3.Connection) -> None:
    """Insert sample data."""
    labels_repo.create_label(conn, Label(id=None, name="Backend"))
    labels_repo.create_label(conn, Label(id=None, name="Frontend"))

    prompts_repo.create_prompt(
        conn,
        Prompt(
            id=None,
            title="Code Review",
            content="Review this code",
            tool="claude",
            is_favorite=True,
            label_ids=[1],
        ),
    )
    commands_repo.create_command(
        conn,
        Command(
            id=None,
            title="Docker Up",
            command_text="docker compose up -d",
            label_ids=[1],
        ),
    )
    api_refs_repo.create_api_ref(
        conn,
        ApiRef(
            id=None,
            service_name="OpenAI",
            base_url="https://api.openai.com/v1",
            auth_type="Bearer Token",
            label_ids=[2],
        ),
    )


def test_export_creates_json(conn: sqlite3.Connection, tmp_path: Path) -> None:
    _seed_data(conn)
    export_file = tmp_path / "export.json"
    export_to_json(conn, export_file)

    assert export_file.exists()
    data = json.loads(export_file.read_text())
    assert data["version"] == "1.6"
    assert len(data["labels"]) == 2
    assert len(data["prompts"]) == 1
    assert len(data["commands"]) == 1
    assert len(data["api_refs"]) == 1


def test_export_preserves_label_names(conn: sqlite3.Connection, tmp_path: Path) -> None:
    _seed_data(conn)
    export_file = tmp_path / "export.json"
    export_to_json(conn, export_file)

    data = json.loads(export_file.read_text())
    prompt = data["prompts"][0]
    assert prompt["label_names"] == ["Backend"]


def test_import_merge(conn: sqlite3.Connection, tmp_path: Path) -> None:
    _seed_data(conn)
    export_file = tmp_path / "export.json"
    export_to_json(conn, export_file)

    # Import in merge mode (labels skipped, others added since no unique constraint)
    counts = import_from_json(conn, export_file, merge=True)
    assert counts["labels"] == 0  # Labels skipped (duplicates)
    assert counts["prompts"] == 1  # Prompts added (no unique constraint)
    assert counts["commands"] == 1
    assert counts["api_refs"] == 1


def test_import_fresh(conn: sqlite3.Connection, tmp_path: Path) -> None:
    _seed_data(conn)
    export_file = tmp_path / "export.json"
    export_to_json(conn, export_file)

    # Clear all data
    conn.execute("DELETE FROM label_items")
    conn.execute("DELETE FROM prompts")
    conn.execute("DELETE FROM commands")
    conn.execute("DELETE FROM api_refs")
    conn.execute("DELETE FROM labels")
    conn.commit()

    # Import fresh
    counts = import_from_json(conn, export_file, merge=False)
    assert counts["labels"] == 2
    assert counts["prompts"] == 1
    assert counts["commands"] == 1
    assert counts["api_refs"] == 1

    # Verify data
    prompts = prompts_repo.list_prompts(conn)
    assert len(prompts) == 1
    assert prompts[0].title == "Code Review"
