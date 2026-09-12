"""Test import/export JSON functionality."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from src.core.io import export_label_to_json, import_label_from_json
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


def _seed_data(conn: sqlite3.Connection) -> int:
    """Insert sample data, return label ID."""
    label = labels_repo.create_label(conn, Label(id=None, name="Backend"))
    assert label.id is not None

    prompts_repo.create_prompt(
        conn,
        Prompt(
            id=None,
            title="Code Review",
            content="Review this code",
            tool="claude",
            is_favorite=True,
        ),
    )
    commands_repo.create_command(
        conn,
        Command(
            id=None,
            title="Docker Up",
            command_text="docker compose up -d",
        ),
    )
    api_refs_repo.create_api_ref(
        conn,
        ApiRef(
            id=None,
            service_name="OpenAI",
            base_url="https://api.openai.com/v1",
            auth_type="Bearer Token",
        ),
    )

    # Assign items to label
    labels_repo.set_item_labels(conn, "prompts", 1, [label.id])
    labels_repo.set_item_labels(conn, "commands", 1, [label.id])

    return label.id


def test_export_label_creates_json(
    conn: sqlite3.Connection, tmp_path: Path
) -> None:
    label_id = _seed_data(conn)
    export_file = tmp_path / "export.json"
    export_label_to_json(conn, export_file, label_id)

    assert export_file.exists()
    data = json.loads(export_file.read_text())
    assert data["label"]["name"] == "Backend"
    assert len(data["prompts"]) == 1
    assert len(data["commands"]) == 1
    assert len(data["api_refs"]) == 0  # Not assigned to label


def test_export_label_preserves_content(
    conn: sqlite3.Connection, tmp_path: Path
) -> None:
    label_id = _seed_data(conn)
    export_file = tmp_path / "export.json"
    export_label_to_json(conn, export_file, label_id)

    data = json.loads(export_file.read_text())
    assert data["prompts"][0]["title"] == "Code Review"
    assert data["prompts"][0]["content"] == "Review this code"
    assert data["commands"][0]["command_text"] == "docker compose up -d"


def test_import_label(conn: sqlite3.Connection, tmp_path: Path) -> None:
    label_id = _seed_data(conn)
    export_file = tmp_path / "export.json"
    export_label_to_json(conn, export_file, label_id)

    # Clear all data
    conn.execute("DELETE FROM label_items")
    conn.execute("DELETE FROM prompts")
    conn.execute("DELETE FROM commands")
    conn.execute("DELETE FROM api_refs")
    conn.execute("DELETE FROM labels")
    conn.commit()

    # Import
    counts = import_label_from_json(conn, export_file)
    assert counts["prompts"] == 1
    assert counts["commands"] == 1
    assert counts["api_refs"] == 0

    # Verify label was created
    labels = labels_repo.list_labels(conn)
    assert len(labels) == 1
    assert labels[0].name == "Backend"

    # Verify items were imported
    prompts = prompts_repo.list_prompts(conn)
    assert len(prompts) == 1
    assert prompts[0].title == "Code Review"


def test_import_label_adds_to_existing(
    conn: sqlite3.Connection, tmp_path: Path
) -> None:
    """Import ke label yang sudah ada, reuse label tapi tambah items."""
    label_id = _seed_data(conn)
    export_file = tmp_path / "export.json"
    export_label_to_json(conn, export_file, label_id)

    # Add more items
    prompts_repo.create_prompt(
        conn, Prompt(id=None, title="Extra", content="extra content")
    )

    # Import (reuses existing label, adds all items from file)
    counts = import_label_from_json(conn, export_file)
    assert counts["prompts"] == 1

    # Verify: 1 original + 1 extra + 1 imported = 3
    prompts = prompts_repo.list_prompts(conn)
    assert len(prompts) == 3

    # Verify label count stays at 1 (reused)
    labels = labels_repo.list_labels(conn)
    assert len(labels) == 1
