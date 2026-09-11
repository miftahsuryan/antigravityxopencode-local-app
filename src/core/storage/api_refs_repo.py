"""Repository CRUD untuk entity ApiRef."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from src.core.models import ApiRef


def _row_to_api_ref(row: sqlite3.Row) -> ApiRef:
    return ApiRef(
        id=row["id"],
        service_name=row["service_name"],
        base_url=row["base_url"],
        description=row["description"],
        auth_type=row["auth_type"],
        keychain_key_name=row["keychain_key_name"],
        tags=json.loads(row["tags"]),
        project_id=row["project_id"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def create_api_ref(conn: sqlite3.Connection, ref: ApiRef) -> ApiRef:
    cur = conn.execute(
        "INSERT INTO api_refs"
        " (service_name, base_url, description, auth_type,"
        " keychain_key_name, tags, project_id)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            ref.service_name,
            ref.base_url,
            ref.description,
            ref.auth_type,
            ref.keychain_key_name,
            json.dumps(ref.tags),
            ref.project_id,
        ),
    )
    conn.commit()
    return _row_to_api_ref(
        conn.execute("SELECT * FROM api_refs WHERE id = ?", (cur.lastrowid,)).fetchone()
    )


def list_api_refs(conn: sqlite3.Connection) -> list[ApiRef]:
    rows = conn.execute("SELECT * FROM api_refs ORDER BY updated_at DESC").fetchall()
    return [_row_to_api_ref(r) for r in rows]


def list_api_refs_by_project(conn: sqlite3.Connection, project_id: int) -> list[ApiRef]:
    rows = conn.execute(
        "SELECT * FROM api_refs WHERE project_id = ? ORDER BY updated_at DESC",
        (project_id,),
    ).fetchall()
    return [_row_to_api_ref(r) for r in rows]


def get_api_ref(conn: sqlite3.Connection, ref_id: int) -> ApiRef | None:
    row = conn.execute("SELECT * FROM api_refs WHERE id = ?", (ref_id,)).fetchone()
    return _row_to_api_ref(row) if row else None


def update_api_ref(conn: sqlite3.Connection, ref: ApiRef) -> ApiRef | None:
    conn.execute(
        """UPDATE api_refs
           SET service_name = ?, base_url = ?, description = ?,
               auth_type = ?, keychain_key_name = ?, tags = ?, project_id = ?,
               updated_at = strftime('%Y-%m-%dT%H:%M:%S','now')
           WHERE id = ?""",
        (
            ref.service_name,
            ref.base_url,
            ref.description,
            ref.auth_type,
            ref.keychain_key_name,
            json.dumps(ref.tags),
            ref.project_id,
            ref.id,
        ),
    )
    conn.commit()
    return get_api_ref(conn, ref.id)  # type: ignore[arg-type]


def delete_api_ref(conn: sqlite3.Connection, ref_id: int) -> bool:
    cur = conn.execute("DELETE FROM api_refs WHERE id = ?", (ref_id,))
    conn.commit()
    return cur.rowcount > 0
