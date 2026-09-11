"""Repository CRUD untuk entity Command."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from src.core.models import Command


def _row_to_command(row: sqlite3.Row) -> Command:
    return Command(
        id=row["id"],
        title=row["title"],
        command_text=row["command_text"],
        description=row["description"],
        tags=json.loads(row["tags"]),
        project_id=row["project_id"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def create_command(conn: sqlite3.Connection, cmd: Command) -> Command:
    cur = conn.execute(
        "INSERT INTO commands (title, command_text, description, tags, project_id) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            cmd.title, cmd.command_text, cmd.description,
            json.dumps(cmd.tags), cmd.project_id,
        ),
    )
    conn.commit()
    return _row_to_command(
        conn.execute("SELECT * FROM commands WHERE id = ?", (cur.lastrowid,)).fetchone()
    )


def list_commands(conn: sqlite3.Connection) -> list[Command]:
    rows = conn.execute("SELECT * FROM commands ORDER BY updated_at DESC").fetchall()
    return [_row_to_command(r) for r in rows]


def list_commands_by_project(
    conn: sqlite3.Connection, project_id: int
) -> list[Command]:
    rows = conn.execute(
        "SELECT * FROM commands WHERE project_id = ? ORDER BY updated_at DESC",
        (project_id,),
    ).fetchall()
    return [_row_to_command(r) for r in rows]


def get_command(conn: sqlite3.Connection, cmd_id: int) -> Command | None:
    row = conn.execute("SELECT * FROM commands WHERE id = ?", (cmd_id,)).fetchone()
    return _row_to_command(row) if row else None


def update_command(conn: sqlite3.Connection, cmd: Command) -> Command | None:
    conn.execute(
        """UPDATE commands
           SET title = ?, command_text = ?, description = ?, tags = ?,
               project_id = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%S','now')
           WHERE id = ?""",
        (
            cmd.title,
            cmd.command_text,
            cmd.description,
            json.dumps(cmd.tags),
            cmd.project_id,
            cmd.id,
        ),
    )
    conn.commit()
    return get_command(conn, cmd.id)  # type: ignore[arg-type]


def delete_command(conn: sqlite3.Connection, cmd_id: int) -> bool:
    cur = conn.execute("DELETE FROM commands WHERE id = ?", (cmd_id,))
    conn.commit()
    return cur.rowcount > 0
