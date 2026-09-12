"""Repository CRUD untuk entity ApiRef."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from src.core.models import ApiRef
from src.core.storage.labels_repo import get_item_label_ids, set_item_labels


def _row_to_api_ref(
    row: sqlite3.Row, conn: sqlite3.Connection | None = None
) -> ApiRef:
    label_ids: list[int] = []
    if conn and row["id"]:
        label_ids = get_item_label_ids(conn, "api_refs", row["id"])
    return ApiRef(
        id=row["id"],
        service_name=row["service_name"],
        base_url=row["base_url"],
        description=row["description"],
        auth_type=row["auth_type"],
        keychain_key_name=row["keychain_key_name"],
        label_ids=label_ids,
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def create_api_ref(conn: sqlite3.Connection, ref: ApiRef) -> ApiRef:
    cur = conn.execute(
        """INSERT INTO api_refs
           (service_name, base_url, description, auth_type, keychain_key_name)
           VALUES (?, ?, ?, ?, ?)""",
        (ref.service_name, ref.base_url, ref.description, ref.auth_type,
         ref.keychain_key_name),
    )
    conn.commit()
    item_id = cur.lastrowid
    assert item_id is not None
    if ref.label_ids:
        set_item_labels(conn, "api_refs", item_id, ref.label_ids)
    row = conn.execute("SELECT * FROM api_refs WHERE id = ?", (item_id,)).fetchone()
    return _row_to_api_ref(row, conn)


def list_api_refs(conn: sqlite3.Connection) -> list[ApiRef]:
    rows = conn.execute("SELECT * FROM api_refs ORDER BY updated_at DESC").fetchall()
    return [_row_to_api_ref(r, conn) for r in rows]


def get_api_ref(conn: sqlite3.Connection, ref_id: int) -> ApiRef | None:
    row = conn.execute("SELECT * FROM api_refs WHERE id = ?", (ref_id,)).fetchone()
    return _row_to_api_ref(row, conn) if row else None


def update_api_ref(conn: sqlite3.Connection, ref: ApiRef) -> ApiRef | None:
    conn.execute(
        """UPDATE api_refs
           SET service_name = ?, base_url = ?, description = ?,
               auth_type = ?, keychain_key_name = ?,
               updated_at = strftime('%Y-%m-%dT%H:%M:%S','now')
           WHERE id = ?""",
        (ref.service_name, ref.base_url, ref.description, ref.auth_type,
         ref.keychain_key_name, ref.id),
    )
    conn.commit()
    if ref.id is not None:
        set_item_labels(conn, "api_refs", ref.id, ref.label_ids)
    return get_api_ref(conn, ref.id)  # type: ignore[arg-type]


def delete_api_ref(conn: sqlite3.Connection, ref_id: int) -> bool:
    conn.execute(
        "DELETE FROM label_items WHERE item_type = 'api_refs' AND item_id = ?",
        (ref_id,),
    )
    cur = conn.execute("DELETE FROM api_refs WHERE id = ?", (ref_id,))
    conn.commit()
    return cur.rowcount > 0
