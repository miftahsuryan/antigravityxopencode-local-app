"""Repository CRUD untuk entity Command."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from src.core.models import Command
from src.core.storage.labels_repo import get_item_label_ids, set_item_labels


def _row_to_command(
    row: sqlite3.Row, conn: sqlite3.Connection | None = None
) -> Command:
    label_ids: list[int] = []
    if conn and row["id"]:
        label_ids = get_item_label_ids(conn, "commands", row["id"])
    return Command(
        id=row["id"],
        title=row["title"],
        command_text=row["command_text"],
        description=row["description"],
        label_ids=label_ids,
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def create_command(conn: sqlite3.Connection, cmd: Command) -> Command:
    cur = conn.execute(
        "INSERT INTO commands (title, command_text, description) "
        "VALUES (?, ?, ?)",
        (cmd.title, cmd.command_text, cmd.description),
    )
    conn.commit()
    item_id = cur.lastrowid
    assert item_id is not None
    if cmd.label_ids:
        set_item_labels(conn, "commands", item_id, cmd.label_ids)
    row = conn.execute("SELECT * FROM commands WHERE id = ?", (item_id,)).fetchone()
    return _row_to_command(row, conn)


def list_commands(conn: sqlite3.Connection) -> list[Command]:
    rows = conn.execute("SELECT * FROM commands ORDER BY updated_at DESC").fetchall()
    return [_row_to_command(r, conn) for r in rows]


def get_command(conn: sqlite3.Connection, cmd_id: int) -> Command | None:
    row = conn.execute("SELECT * FROM commands WHERE id = ?", (cmd_id,)).fetchone()
    return _row_to_command(row, conn) if row else None


def update_command(conn: sqlite3.Connection, cmd: Command) -> Command | None:
    conn.execute(
        """UPDATE commands
           SET title = ?, command_text = ?, description = ?,
               updated_at = strftime('%Y-%m-%dT%H:%M:%S','now')
           WHERE id = ?""",
        (cmd.title, cmd.command_text, cmd.description, cmd.id),
    )
    conn.commit()
    if cmd.id is not None:
        set_item_labels(conn, "commands", cmd.id, cmd.label_ids)
    return get_command(conn, cmd.id)  # type: ignore[arg-type]


def delete_command(conn: sqlite3.Connection, cmd_id: int) -> bool:
    conn.execute(
        "DELETE FROM label_items WHERE item_type = 'commands' AND item_id = ?",
        (cmd_id,),
    )
    cur = conn.execute("DELETE FROM commands WHERE id = ?", (cmd_id,))
    conn.commit()
    return cur.rowcount > 0
