"""Repository CRUD untuk entity Project."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from src.core.models import Project


def _row_to_project(row: sqlite3.Row) -> Project:
    return Project(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def create_project(conn: sqlite3.Connection, project: Project) -> Project:
    cur = conn.execute(
        "INSERT INTO projects (name, description) VALUES (?, ?)",
        (project.name, project.description),
    )
    conn.commit()
    return _row_to_project(
        conn.execute("SELECT * FROM projects WHERE id = ?", (cur.lastrowid,)).fetchone()
    )


def list_projects(conn: sqlite3.Connection) -> list[Project]:
    rows = conn.execute("SELECT * FROM projects ORDER BY updated_at DESC").fetchall()
    return [_row_to_project(r) for r in rows]


def get_project(conn: sqlite3.Connection, project_id: int) -> Project | None:
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    return _row_to_project(row) if row else None


def update_project(conn: sqlite3.Connection, project: Project) -> Project | None:
    conn.execute(
        """UPDATE projects
           SET name = ?, description = ?,
           updated_at = strftime('%Y-%m-%dT%H:%M:%S','now')
           WHERE id = ?""",
        (project.name, project.description, project.id),
    )
    conn.commit()
    return get_project(conn, project.id)


def delete_project(conn: sqlite3.Connection, project_id: int) -> bool:
    cur = conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    return cur.rowcount > 0
