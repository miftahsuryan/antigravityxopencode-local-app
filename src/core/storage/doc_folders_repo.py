"""Repository CRUD untuk entity DocFolder."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from src.core.models import DocFolder
from src.core.storage.labels_repo import get_item_label_ids, set_item_labels


def _row_to_folder(
    row: sqlite3.Row, conn: sqlite3.Connection | None = None
) -> DocFolder:
    label_ids: list[int] = []
    if conn and row["id"]:
        label_ids = get_item_label_ids(conn, "doc_folders", row["id"])
    return DocFolder(
        id=row["id"],
        name=row["name"],
        parent_id=row["parent_id"],
        color=row["color"],
        label_ids=label_ids,
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def create_folder(conn: sqlite3.Connection, folder: DocFolder) -> DocFolder:
    cur = conn.execute(
        "INSERT INTO doc_folders (name, parent_id, color) VALUES (?, ?, ?)",
        (folder.name, folder.parent_id, folder.color),
    )
    conn.commit()
    item_id = cur.lastrowid
    assert item_id is not None
    if folder.label_ids:
        set_item_labels(conn, "doc_folders", item_id, folder.label_ids)
    row = conn.execute(
        "SELECT * FROM doc_folders WHERE id = ?", (item_id,)
    ).fetchone()
    return _row_to_folder(row, conn)


def list_root_folders(conn: sqlite3.Connection) -> list[DocFolder]:
    rows = conn.execute(
        "SELECT * FROM doc_folders WHERE parent_id IS NULL ORDER BY name ASC"
    ).fetchall()
    return [_row_to_folder(r, conn) for r in rows]


def get_children(conn: sqlite3.Connection, parent_id: int) -> list[DocFolder]:
    rows = conn.execute(
        "SELECT * FROM doc_folders WHERE parent_id = ? ORDER BY name ASC",
        (parent_id,),
    ).fetchall()
    return [_row_to_folder(r, conn) for r in rows]


def get_folder(conn: sqlite3.Connection, folder_id: int) -> DocFolder | None:
    row = conn.execute(
        "SELECT * FROM doc_folders WHERE id = ?", (folder_id,)
    ).fetchone()
    return _row_to_folder(row, conn) if row else None


def get_folder_depth(conn: sqlite3.Connection, folder_id: int) -> int:
    depth = 0
    current_id: int | None = folder_id
    while current_id is not None:
        row = conn.execute(
            "SELECT parent_id FROM doc_folders WHERE id = ?", (current_id,)
        ).fetchone()
        if row is None:
            break
        current_id = row["parent_id"]
        if current_id is not None:
            depth += 1
    return depth


def update_folder(conn: sqlite3.Connection, folder: DocFolder) -> DocFolder | None:
    conn.execute(
        """UPDATE doc_folders
           SET name = ?, parent_id = ?, color = ?,
               updated_at = strftime('%Y-%m-%dT%H:%M:%S','now')
           WHERE id = ?""",
        (folder.name, folder.parent_id, folder.color, folder.id),
    )
    conn.commit()
    if folder.id is not None:
        set_item_labels(conn, "doc_folders", folder.id, folder.label_ids)
    return get_folder(conn, folder.id)  # type: ignore[arg-type]


def delete_folder(conn: sqlite3.Connection, folder_id: int) -> bool:
    conn.execute(
        "DELETE FROM label_items WHERE item_type = 'doc_folders' AND item_id = ?",
        (folder_id,),
    )
    cur = conn.execute("DELETE FROM doc_folders WHERE id = ?", (folder_id,))
    conn.commit()
    return cur.rowcount > 0


def count_files_in_folder(conn: sqlite3.Connection, folder_id: int) -> int:
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM doc_files WHERE folder_id = ?", (folder_id,)
    ).fetchone()
    return row["cnt"] if row else 0


def count_all_folders(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT COUNT(*) as cnt FROM doc_folders").fetchone()
    return row["cnt"] if row else 0
