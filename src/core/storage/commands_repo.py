"""Repository CRUD untuk entity Command."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from src.core.models import Command


def _row_to_command(row: sqlite3.Row) -> Command:
    """Konversi sqlite3.Row menjadi dataclass Command."""
    return Command(
        id=row["id"],
        title=row["title"],
        command_text=row["command_text"],
        description=row["description"],
        tags=json.loads(row["tags"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def create_command(conn: sqlite3.Connection, cmd: Command) -> Command:
    """Simpan command baru ke DB.

    Args:
        conn: koneksi SQLite.
        cmd: instance Command (id boleh None).

    Returns:
        Command dengan id yang sudah terisi.
    """
    cur = conn.execute(
        """INSERT INTO commands (title, command_text, description, tags)
           VALUES (?, ?, ?, ?)""",
        (cmd.title, cmd.command_text, cmd.description, json.dumps(cmd.tags)),
    )
    conn.commit()
    return _row_to_command(
        conn.execute("SELECT * FROM commands WHERE id = ?", (cur.lastrowid,)).fetchone()
    )


def list_commands(conn: sqlite3.Connection) -> list[Command]:
    """Ambil semua command, urut terbaru dulu.

    Args:
        conn: koneksi SQLite.

    Returns:
        Daftar Command.
    """
    rows = conn.execute("SELECT * FROM commands ORDER BY updated_at DESC").fetchall()
    return [_row_to_command(r) for r in rows]


def get_command(conn: sqlite3.Connection, cmd_id: int) -> Command | None:
    """Ambil satu command berdasarkan ID.

    Args:
        conn: koneksi SQLite.
        cmd_id: primary key.

    Returns:
        Command atau None kalau tidak ditemukan.
    """
    row = conn.execute("SELECT * FROM commands WHERE id = ?", (cmd_id,)).fetchone()
    return _row_to_command(row) if row else None


def update_command(conn: sqlite3.Connection, cmd: Command) -> Command | None:
    """Update command yang sudah ada.

    Args:
        conn: koneksi SQLite.
        cmd: instance Command dengan id terisi.

    Returns:
        Command yang sudah di-update, atau None kalau id tidak ditemukan.
    """
    conn.execute(
        """UPDATE commands
           SET title = ?, command_text = ?, description = ?, tags = ?,
               updated_at = strftime('%Y-%m-%dT%H:%M:%S','now')
         WHERE id = ?""",
        (
            cmd.title,
            cmd.command_text,
            cmd.description,
            json.dumps(cmd.tags),
            cmd.id,
        ),
    )
    conn.commit()
    return get_command(conn, cmd.id)  # type: ignore[arg-type]


def delete_command(conn: sqlite3.Connection, cmd_id: int) -> bool:
    """Hapus command berdasarkan ID.

    Args:
        conn: koneksi SQLite.
        cmd_id: primary key.

    Returns:
        True kalau berhasil dihapus, False kalau tidak ditemukan.
    """
    cur = conn.execute("DELETE FROM commands WHERE id = ?", (cmd_id,))
    conn.commit()
    return cur.rowcount > 0
