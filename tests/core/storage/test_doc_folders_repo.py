"""Test CRUD doc_folders_repo."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.core.models import DocFolder
from src.core.storage.db import init_db
from src.core.storage.doc_folders_repo import (
    count_all_folders,
    count_files_in_folder,
    create_folder,
    delete_folder,
    get_children,
    get_folder,
    get_folder_depth,
    list_root_folders,
    update_folder,
)


@pytest.fixture()
def conn(tmp_path: Path) -> sqlite3.Connection:
    return init_db(tmp_path / "test.db")


def test_create_and_get_folder(conn: sqlite3.Connection) -> None:
    folder = DocFolder(id=None, name="Guides", color="#2DD4BF")
    saved = create_folder(conn, folder)
    assert saved.id is not None
    assert saved.name == "Guides"
    assert saved.color == "#2DD4BF"

    fetched = get_folder(conn, saved.id)
    assert fetched is not None
    assert fetched.name == "Guides"


def test_list_root_folders(conn: sqlite3.Connection) -> None:
    root = create_folder(conn, DocFolder(id=None, name="Root"))
    child = create_folder(
        conn, DocFolder(id=None, name="Child", parent_id=root.id)
    )
    roots = list_root_folders(conn)
    assert len(roots) == 1
    assert roots[0].id == root.id


def test_get_children(conn: sqlite3.Connection) -> None:
    root = create_folder(conn, DocFolder(id=None, name="Root"))
    c1 = create_folder(
        conn, DocFolder(id=None, name="A", parent_id=root.id)
    )
    c2 = create_folder(
        conn, DocFolder(id=None, name="B", parent_id=root.id)
    )
    children = get_children(conn, root.id)  # type: ignore[arg-type]
    assert len(children) == 2
    ids = {c.id for c in children}
    assert c1.id in ids
    assert c2.id in ids


def test_update_folder(conn: sqlite3.Connection) -> None:
    folder = create_folder(conn, DocFolder(id=None, name="Old"))
    folder.name = "New"
    folder.color = "#F5A623"
    updated = update_folder(conn, folder)
    assert updated is not None
    assert updated.name == "New"
    assert updated.color == "#F5A623"


def test_delete_folder(conn: sqlite3.Connection) -> None:
    folder = create_folder(conn, DocFolder(id=None, name="Delete Me"))
    assert delete_folder(conn, folder.id) is True  # type: ignore[arg-type]
    assert get_folder(conn, folder.id) is None  # type: ignore[arg-type]


def test_delete_folder_cascades_to_children(conn: sqlite3.Connection) -> None:
    root = create_folder(conn, DocFolder(id=None, name="Root"))
    child = create_folder(
        conn, DocFolder(id=None, name="Child", parent_id=root.id)
    )
    delete_folder(conn, root.id)  # type: ignore[arg-type]
    assert get_folder(conn, child.id) is None


def test_folder_depth(conn: sqlite3.Connection) -> None:
    root = create_folder(conn, DocFolder(id=None, name="L1"))
    l2 = create_folder(
        conn, DocFolder(id=None, name="L2", parent_id=root.id)
    )
    l3 = create_folder(
        conn, DocFolder(id=None, name="L3", parent_id=l2.id)
    )
    assert get_folder_depth(conn, root.id) == 0  # type: ignore[arg-type]
    assert get_folder_depth(conn, l2.id) == 1  # type: ignore[arg-type]
    assert get_folder_depth(conn, l3.id) == 2  # type: ignore[arg-type]


def test_count_files_in_folder(conn: sqlite3.Connection) -> None:
    folder = create_folder(conn, DocFolder(id=None, name="Docs"))
    assert count_files_in_folder(conn, folder.id) == 0  # type: ignore[arg-type]


def test_count_all_folders(conn: sqlite3.Connection) -> None:
    assert count_all_folders(conn) == 0
    create_folder(conn, DocFolder(id=None, name="A"))
    create_folder(conn, DocFolder(id=None, name="B"))
    assert count_all_folders(conn) == 2


def test_get_nonexistent_returns_none(conn: sqlite3.Connection) -> None:
    assert get_folder(conn, 9999) is None
