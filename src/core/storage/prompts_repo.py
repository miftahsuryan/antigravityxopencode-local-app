"""Repository CRUD untuk entity Prompt."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from src.core.models import Prompt
from src.core.storage.labels_repo import get_item_label_ids, set_item_labels


def _row_to_prompt(row: sqlite3.Row, conn: sqlite3.Connection | None = None) -> Prompt:
    label_ids: list[int] = []
    if conn and row["id"]:
        label_ids = get_item_label_ids(conn, "prompts", row["id"])
    return Prompt(
        id=row["id"],
        title=row["title"],
        content=row["content"],
        tool=row["tool"],
        is_favorite=bool(row["is_favorite"]),
        label_ids=label_ids,
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def create_prompt(conn: sqlite3.Connection, prompt: Prompt) -> Prompt:
    cur = conn.execute(
        "INSERT INTO prompts (title, content, tool, is_favorite) "
        "VALUES (?, ?, ?, ?)",
        (prompt.title, prompt.content, prompt.tool, int(prompt.is_favorite)),
    )
    conn.commit()
    item_id = cur.lastrowid
    assert item_id is not None
    if prompt.label_ids:
        set_item_labels(conn, "prompts", item_id, prompt.label_ids)
    row = conn.execute("SELECT * FROM prompts WHERE id = ?", (item_id,)).fetchone()
    return _row_to_prompt(row, conn)


def list_prompts(conn: sqlite3.Connection) -> list[Prompt]:
    rows = conn.execute("SELECT * FROM prompts ORDER BY updated_at DESC").fetchall()
    return [_row_to_prompt(r, conn) for r in rows]


def get_prompt(conn: sqlite3.Connection, prompt_id: int) -> Prompt | None:
    row = conn.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,)).fetchone()
    return _row_to_prompt(row, conn) if row else None


def update_prompt(conn: sqlite3.Connection, prompt: Prompt) -> Prompt | None:
    conn.execute(
        """UPDATE prompts
           SET title = ?, content = ?, tool = ?, is_favorite = ?,
               updated_at = strftime('%Y-%m-%dT%H:%M:%S','now')
           WHERE id = ?""",
        (prompt.title, prompt.content, prompt.tool, int(prompt.is_favorite), prompt.id),
    )
    conn.commit()
    if prompt.id is not None:
        set_item_labels(conn, "prompts", prompt.id, prompt.label_ids)
    return get_prompt(conn, prompt.id)  # type: ignore[arg-type]


def delete_prompt(conn: sqlite3.Connection, prompt_id: int) -> bool:
    conn.execute(
        "DELETE FROM label_items WHERE item_type = 'prompts' AND item_id = ?",
        (prompt_id,),
    )
    cur = conn.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
    conn.commit()
    return cur.rowcount > 0
