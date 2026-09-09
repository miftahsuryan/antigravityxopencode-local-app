"""Repository CRUD untuk entity Prompt."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from src.core.models import Prompt


def _row_to_prompt(row: sqlite3.Row) -> Prompt:
    """Konversi sqlite3.Row menjadi dataclass Prompt."""
    return Prompt(
        id=row["id"],
        title=row["title"],
        content=row["content"],
        tool=row["tool"],
        tags=json.loads(row["tags"]),
        is_favorite=bool(row["is_favorite"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def create_prompt(conn: sqlite3.Connection, prompt: Prompt) -> Prompt:
    """Simpan prompt baru ke DB.

    Args:
        conn: koneksi SQLite.
        prompt: instance Prompt (id boleh None).

    Returns:
        Prompt dengan id yang sudah terisi.
    """
    cur = conn.execute(
        """INSERT INTO prompts (title, content, tool, tags, is_favorite)
           VALUES (?, ?, ?, ?, ?)""",
        (
            prompt.title,
            prompt.content,
            prompt.tool,
            json.dumps(prompt.tags),
            int(prompt.is_favorite),
        ),
    )
    conn.commit()
    return _row_to_prompt(
        conn.execute("SELECT * FROM prompts WHERE id = ?", (cur.lastrowid,)).fetchone()
    )


def list_prompts(conn: sqlite3.Connection) -> list[Prompt]:
    """Ambil semua prompt, urut terbaru dulu.

    Args:
        conn: koneksi SQLite.

    Returns:
        Daftar Prompt.
    """
    rows = conn.execute("SELECT * FROM prompts ORDER BY updated_at DESC").fetchall()
    return [_row_to_prompt(r) for r in rows]


def get_prompt(conn: sqlite3.Connection, prompt_id: int) -> Prompt | None:
    """Ambil satu prompt berdasarkan ID.

    Args:
        conn: koneksi SQLite.
        prompt_id: primary key.

    Returns:
        Prompt atau None kalau tidak ditemukan.
    """
    row = conn.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,)).fetchone()
    return _row_to_prompt(row) if row else None


def update_prompt(conn: sqlite3.Connection, prompt: Prompt) -> Prompt | None:
    """Update prompt yang sudah ada.

    Args:
        conn: koneksi SQLite.
        prompt: instance Prompt dengan id terisi.

    Returns:
        Prompt yang sudah di-update, atau None kalau id tidak ditemukan.
    """
    conn.execute(
        """UPDATE prompts
           SET title = ?, content = ?, tool = ?, tags = ?, is_favorite = ?,
               updated_at = strftime('%Y-%m-%dT%H:%M:%S','now')
         WHERE id = ?""",
        (
            prompt.title,
            prompt.content,
            prompt.tool,
            json.dumps(prompt.tags),
            int(prompt.is_favorite),
            prompt.id,
        ),
    )
    conn.commit()
    return get_prompt(conn, prompt.id)  # type: ignore[arg-type]


def delete_prompt(conn: sqlite3.Connection, prompt_id: int) -> bool:
    """Hapus prompt berdasarkan ID.

    Args:
        conn: koneksi SQLite.
        prompt_id: primary key.

    Returns:
        True kalau berhasil dihapus, False kalau tidak ditemukan.
    """
    cur = conn.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
    conn.commit()
    return cur.rowcount > 0
