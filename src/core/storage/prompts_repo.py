"""Repository CRUD untuk entity Prompt."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from src.core.models import Prompt


def _row_to_prompt(row: sqlite3.Row) -> Prompt:
    return Prompt(
        id=row["id"],
        title=row["title"],
        content=row["content"],
        tool=row["tool"],
        tags=json.loads(row["tags"]),
        is_favorite=bool(row["is_favorite"]),
        project_id=row["project_id"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def create_prompt(conn: sqlite3.Connection, prompt: Prompt) -> Prompt:
    cur = conn.execute(
        "INSERT INTO prompts (title, content, tool, tags, is_favorite, project_id) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            prompt.title,
            prompt.content,
            prompt.tool,
            json.dumps(prompt.tags),
            int(prompt.is_favorite),
            prompt.project_id,
        ),
    )
    conn.commit()
    return _row_to_prompt(
        conn.execute("SELECT * FROM prompts WHERE id = ?", (cur.lastrowid,)).fetchone()
    )


def list_prompts(conn: sqlite3.Connection) -> list[Prompt]:
    rows = conn.execute("SELECT * FROM prompts ORDER BY updated_at DESC").fetchall()
    return [_row_to_prompt(r) for r in rows]


def list_prompts_by_project(conn: sqlite3.Connection, project_id: int) -> list[Prompt]:
    rows = conn.execute(
        "SELECT * FROM prompts WHERE project_id = ? ORDER BY updated_at DESC",
        (project_id,),
    ).fetchall()
    return [_row_to_prompt(r) for r in rows]


def get_prompt(conn: sqlite3.Connection, prompt_id: int) -> Prompt | None:
    row = conn.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,)).fetchone()
    return _row_to_prompt(row) if row else None


def update_prompt(conn: sqlite3.Connection, prompt: Prompt) -> Prompt | None:
    conn.execute(
        """UPDATE prompts
           SET title = ?, content = ?, tool = ?, tags = ?, is_favorite = ?,
               project_id = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%S','now')
           WHERE id = ?""",
        (
            prompt.title,
            prompt.content,
            prompt.tool,
            json.dumps(prompt.tags),
            int(prompt.is_favorite),
            prompt.project_id,
            prompt.id,
        ),
    )
    conn.commit()
    return get_prompt(conn, prompt.id)  # type: ignore[arg-type]


def delete_prompt(conn: sqlite3.Connection, prompt_id: int) -> bool:
    cur = conn.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
    conn.commit()
    return cur.rowcount > 0
