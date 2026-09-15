"""Test CRUD doc_files_repo."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.core.models import DocFile, DocFolder
from src.core.storage.db import init_db
from src.core.storage import doc_files_repo, doc_folders_repo


@pytest.fixture()
def conn(tmp_path: Path) -> sqlite3.Connection:
    return init_db(tmp_path / "test.db")


def test_create_and_get_file(conn: sqlite3.Connection) -> None:
    doc_file = DocFile(
        id=None, title="readme.md", content="# Hello"
    )
    saved = doc_files_repo.create_file(conn, doc_file)
    assert saved.id is not None
    assert saved.title == "readme.md"
    assert saved.content == "# Hello"
    assert saved.file_type == "md"

    fetched = doc_files_repo.get_file(conn, saved.id)
    assert fetched is not None
    assert fetched.content == "# Hello"


def test_list_files_by_folder(conn: sqlite3.Connection) -> None:
    folder = doc_folders_repo.create_folder(
        conn, DocFolder(id=None, name="Notes")
    )
    doc_files_repo.create_file(
        conn, DocFile(id=None, title="a.md", folder_id=folder.id)
    )
    doc_files_repo.create_file(
        conn, DocFile(id=None, title="b.md", folder_id=folder.id)
    )
    files = doc_files_repo.list_files_by_folder(conn, folder.id)
    assert len(files) == 2


def test_list_root_files(conn: sqlite3.Connection) -> None:
    doc_files_repo.create_file(
        conn, DocFile(id=None, title="root.md", folder_id=None)
    )
    files = doc_files_repo.list_files_by_folder(conn, None)
    assert len(files) == 1
    assert files[0].title == "root.md"


def test_update_file(conn: sqlite3.Connection) -> None:
    doc_file = doc_files_repo.create_file(
        conn, DocFile(id=None, title="old.md", content="old")
    )
    doc_file.content = "new content"
    updated = doc_files_repo.update_file(conn, doc_file)
    assert updated is not None
    assert updated.content == "new content"


def test_delete_file(conn: sqlite3.Connection) -> None:
    doc_file = doc_files_repo.create_file(
        conn, DocFile(id=None, title="delete.md")
    )
    assert doc_files_repo.delete_file(conn, doc_file.id) is True  # type: ignore[arg-type]
    assert doc_files_repo.get_file(conn, doc_file.id) is None  # type: ignore[arg-type]


def test_delete_folder_cascades_files(conn: sqlite3.Connection) -> None:
    folder = doc_folders_repo.create_folder(
        conn, DocFolder(id=None, name="Docs")
    )
    doc_files_repo.create_file(
        conn, DocFile(id=None, title="f.md", folder_id=folder.id)
    )
    doc_folders_repo.delete_folder(conn, folder.id)  # type: ignore[arg-type]
    files = doc_files_repo.list_files_by_folder(conn, folder.id)
    assert len(files) == 0


def test_count_all_files(conn: sqlite3.Connection) -> None:
    assert doc_files_repo.count_all_files(conn) == 0
    doc_files_repo.create_file(conn, DocFile(id=None, title="a.md"))
    doc_files_repo.create_file(conn, DocFile(id=None, title="b.md"))
    assert doc_files_repo.count_all_files(conn) == 2


def test_get_nonexistent_returns_none(conn: sqlite3.Connection) -> None:
    assert doc_files_repo.get_file(conn, 9999) is None
