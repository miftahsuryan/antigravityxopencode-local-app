"""Repository CRUD untuk entity DocFile."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from src.core.models import DocFile


def _row_to_file(row: sqlite3.Row) -> DocFile:
    return DocFile(
        id=row["id"],
        title=row["title"],
        content=row["content"],
        folder_id=row["folder_id"],
        file_type=row["file_type"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def create_file(conn: sqlite3.Connection, doc_file: DocFile) -> DocFile:
    cur = conn.execute(
        "INSERT INTO doc_files (title, content, folder_id, file_type) "
        "VALUES (?, ?, ?, ?)",
        (doc_file.title, doc_file.content, doc_file.folder_id, doc_file.file_type),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM doc_files WHERE id = ?", (cur.lastrowid,)
    ).fetchone()
    return _row_to_file(row)


def list_files_by_folder(
    conn: sqlite3.Connection, folder_id: int | None
) -> list[DocFile]:
    if folder_id is None:
        rows = conn.execute(
            "SELECT * FROM doc_files WHERE folder_id IS NULL "
            "ORDER BY updated_at DESC"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM doc_files WHERE folder_id = ? "
            "ORDER BY updated_at DESC",
            (folder_id,),
        ).fetchall()
    return [_row_to_file(r) for r in rows]


def get_file(conn: sqlite3.Connection, file_id: int) -> DocFile | None:
    row = conn.execute(
        "SELECT * FROM doc_files WHERE id = ?", (file_id,)
    ).fetchone()
    return _row_to_file(row) if row else None


def update_file(conn: sqlite3.Connection, doc_file: DocFile) -> DocFile | None:
    conn.execute(
        """UPDATE doc_files
           SET title = ?, content = ?, folder_id = ?, file_type = ?,
               updated_at = strftime('%Y-%m-%dT%H:%M:%S','now')
           WHERE id = ?""",
        (
            doc_file.title,
            doc_file.content,
            doc_file.folder_id,
            doc_file.file_type,
            doc_file.id,
        ),
    )
    conn.commit()
    return get_file(conn, doc_file.id)  # type: ignore[arg-type]


def delete_file(conn: sqlite3.Connection, file_id: int) -> bool:
    cur = conn.execute("DELETE FROM doc_files WHERE id = ?", (file_id,))
    conn.commit()
    return cur.rowcount > 0


def count_all_files(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT COUNT(*) as cnt FROM doc_files").fetchone()
    return row["cnt"] if row else 0
