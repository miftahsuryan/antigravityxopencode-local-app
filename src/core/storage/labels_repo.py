"""Repository CRUD untuk entity Label + junction label_items."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from src.core.models import Label


def _row_to_label(row: sqlite3.Row) -> Label:
    return Label(
        id=row["id"],
        name=row["name"],
        color=row["color"],
        description=row["description"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def create_label(conn: sqlite3.Connection, label: Label) -> Label:
    cur = conn.execute(
        "INSERT INTO labels (name, color, description) VALUES (?, ?, ?)",
        (label.name, label.color, label.description),
    )
    conn.commit()
    return _row_to_label(
        conn.execute("SELECT * FROM labels WHERE id = ?", (cur.lastrowid,)).fetchone()
    )


def list_labels(conn: sqlite3.Connection) -> list[Label]:
    rows = conn.execute("SELECT * FROM labels ORDER BY name ASC").fetchall()
    return [_row_to_label(r) for r in rows]


def get_label(conn: sqlite3.Connection, label_id: int) -> Label | None:
    row = conn.execute("SELECT * FROM labels WHERE id = ?", (label_id,)).fetchone()
    return _row_to_label(row) if row else None


def update_label(conn: sqlite3.Connection, label: Label) -> Label | None:
    conn.execute(
        """UPDATE labels
           SET name = ?, color = ?, description = ?,
           updated_at = strftime('%Y-%m-%dT%H:%M:%S','now')
           WHERE id = ?""",
        (label.name, label.color, label.description, label.id),
    )
    conn.commit()
    return get_label(conn, label.id)  # type: ignore[arg-type]


def delete_label(conn: sqlite3.Connection, label_id: int) -> bool:
    cur = conn.execute("DELETE FROM labels WHERE id = ?", (label_id,))
    conn.execute("DELETE FROM label_items WHERE label_id = ?", (label_id,))
    conn.commit()
    return cur.rowcount > 0


# --- Junction table helpers ---


def set_item_labels(
    conn: sqlite3.Connection, item_type: str, item_id: int, label_ids: list[int]
) -> None:
    conn.execute(
        "DELETE FROM label_items WHERE item_type = ? AND item_id = ?",
        (item_type, item_id),
    )
    for lid in label_ids:
        conn.execute(
            "INSERT OR IGNORE INTO label_items (label_id, item_type, item_id) "
            "VALUES (?, ?, ?)",
            (lid, item_type, item_id),
        )
    conn.commit()


def get_item_label_ids(
    conn: sqlite3.Connection, item_type: str, item_id: int
) -> list[int]:
    rows = conn.execute(
        "SELECT label_id FROM label_items WHERE item_type = ? AND item_id = ?",
        (item_type, item_id),
    ).fetchall()
    return [r["label_id"] for r in rows]


def get_items_by_label(
    conn: sqlite3.Connection, label_id: int, item_type: str
) -> list[int]:
    rows = conn.execute(
        "SELECT item_id FROM label_items WHERE label_id = ? AND item_type = ?",
        (label_id, item_type),
    ).fetchall()
    return [r["item_id"] for r in rows]


def get_labels_for_item(
    conn: sqlite3.Connection, item_type: str, item_id: int
) -> list[Label]:
    rows = conn.execute(
        """SELECT l.* FROM labels l
           JOIN label_items li ON l.id = li.label_id
           WHERE li.item_type = ? AND li.item_id = ?
           ORDER BY l.name""",
        (item_type, item_id),
    ).fetchall()
    return [_row_to_label(r) for r in rows]


def get_label_item_counts(conn: sqlite3.Connection) -> dict[int, dict[str, int]]:
    counts: dict[int, dict[str, int]] = {}
    rows = conn.execute(
        "SELECT label_id, item_type, COUNT(*) as cnt "
        "FROM label_items GROUP BY label_id, item_type"
    ).fetchall()
    for r in rows:
        lid = r["label_id"]
        if lid not in counts:
            counts[lid] = {"prompts": 0, "commands": 0, "api_refs": 0}
        counts[lid][r["item_type"]] = r["cnt"]
    return counts
