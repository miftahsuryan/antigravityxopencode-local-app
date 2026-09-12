"""Test labels_repo: CRUD + junction table operations."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.core.models import Label
from src.core.storage.db import init_db
from src.core.storage.labels_repo import (
    create_label,
    delete_label,
    get_label,
    get_label_item_counts,
    get_item_label_ids,
    get_items_by_label,
    get_labels_for_item,
    list_labels,
    set_item_labels,
    update_label,
)


@pytest.fixture()
def conn(tmp_path: Path) -> sqlite3.Connection:
    return init_db(tmp_path / "test.db")


def test_create_and_get_label(conn: sqlite3.Connection) -> None:
    label = create_label(conn, Label(id=None, name="Backend", color="#FF0000"))
    assert label.id is not None
    assert label.name == "Backend"
    assert label.color == "#FF0000"

    fetched = get_label(conn, label.id)
    assert fetched is not None
    assert fetched.name == "Backend"


def test_list_labels(conn: sqlite3.Connection) -> None:
    create_label(conn, Label(id=None, name="Alpha"))
    create_label(conn, Label(id=None, name="Beta"))
    labels = list_labels(conn)
    assert len(labels) == 2
    # Sorted by name
    assert labels[0].name == "Alpha"
    assert labels[1].name == "Beta"


def test_update_label(conn: sqlite3.Connection) -> None:
    label = create_label(conn, Label(id=None, name="Old"))
    label.name = "New"
    label.color = "#00FF00"
    updated = update_label(conn, label)
    assert updated is not None
    assert updated.name == "New"
    assert updated.color == "#00FF00"


def test_delete_label(conn: sqlite3.Connection) -> None:
    label = create_label(conn, Label(id=None, name="Delete Me"))
    assert delete_label(conn, label.id) is True
    assert get_label(conn, label.id) is None


def test_label_name_unique(conn: sqlite3.Connection) -> None:
    create_label(conn, Label(id=None, name="Unique"))
    with pytest.raises(sqlite3.IntegrityError):
        create_label(conn, Label(id=None, name="Unique"))


def test_set_and_get_item_labels(conn: sqlite3.Connection) -> None:
    label1 = create_label(conn, Label(id=None, name="L1"))
    label2 = create_label(conn, Label(id=None, name="L2"))

    set_item_labels(conn, "prompts", 1, [label1.id, label2.id])
    ids = get_item_label_ids(conn, "prompts", 1)
    assert set(ids) == {label1.id, label2.id}


def test_set_item_labels_replaces(conn: sqlite3.Connection) -> None:
    label1 = create_label(conn, Label(id=None, name="L1"))
    label2 = create_label(conn, Label(id=None, name="L2"))

    set_item_labels(conn, "prompts", 1, [label1.id])
    set_item_labels(conn, "prompts", 1, [label2.id])
    ids = get_item_label_ids(conn, "prompts", 1)
    assert ids == [label2.id]


def test_get_items_by_label(conn: sqlite3.Connection) -> None:
    label = create_label(conn, Label(id=None, name="Test"))
    set_item_labels(conn, "prompts", 1, [label.id])
    set_item_labels(conn, "prompts", 2, [label.id])
    set_item_labels(conn, "commands", 1, [label.id])

    prompt_ids = get_items_by_label(conn, label.id, "prompts")
    assert set(prompt_ids) == {1, 2}

    cmd_ids = get_items_by_label(conn, label.id, "commands")
    assert cmd_ids == [1]


def test_get_labels_for_item(conn: sqlite3.Connection) -> None:
    l1 = create_label(conn, Label(id=None, name="L1"))
    l2 = create_label(conn, Label(id=None, name="L2"))
    set_item_labels(conn, "prompts", 1, [l1.id, l2.id])

    labels = get_labels_for_item(conn, "prompts", 1)
    assert len(labels) == 2
    names = {lb.name for lb in labels}
    assert names == {"L1", "L2"}


def test_get_label_item_counts(conn: sqlite3.Connection) -> None:
    l1 = create_label(conn, Label(id=None, name="L1"))
    set_item_labels(conn, "prompts", 1, [l1.id])
    set_item_labels(conn, "prompts", 2, [l1.id])
    set_item_labels(conn, "commands", 1, [l1.id])

    counts = get_label_item_counts(conn)
    assert counts[l1.id]["prompts"] == 2
    assert counts[l1.id]["commands"] == 1
    assert counts[l1.id]["api_refs"] == 0
