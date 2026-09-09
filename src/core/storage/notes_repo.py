"""Repository CRUD untuk entity Note.

Konten Markdown tetap disimpan sebagai file .md di vault.
Tabel ``notes`` di SQLite hanya menyimpan metadata/index.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from src.core.models import Note


def _row_to_note(row: sqlite3.Row) -> Note:
    """Konversi sqlite3.Row menjadi dataclass Note."""
    return Note(
        id=row["id"],
        title=row["title"],
        file_path=row["file_path"],
        tags=json.loads(row["tags"]),
        folder=row["folder"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def create_note(conn: sqlite3.Connection, note: Note) -> Note:
    """Simpan metadata note baru ke DB.

    Args:
        conn: koneksi SQLite.
        note: instance Note (id boleh None).

    Returns:
        Note dengan id yang sudah terisi.
    """
    cur = conn.execute(
        "INSERT INTO notes (title, file_path, tags, folder) VALUES (?, ?, ?, ?)",
        (note.title, note.file_path, json.dumps(note.tags), note.folder),
    )
    conn.commit()
    return _row_to_note(
        conn.execute("SELECT * FROM notes WHERE id = ?", (cur.lastrowid,)).fetchone()
    )


def list_notes(conn: sqlite3.Connection) -> list[Note]:
    """Ambil semua note, urut terbaru dulu.

    Args:
        conn: koneksi SQLite.

    Returns:
        Daftar Note.
    """
    rows = conn.execute("SELECT * FROM notes ORDER BY updated_at DESC").fetchall()
    return [_row_to_note(r) for r in rows]


def get_note(conn: sqlite3.Connection, note_id: int) -> Note | None:
    """Ambil satu note berdasarkan ID.

    Args:
        conn: koneksi SQLite.
        note_id: primary key.

    Returns:
        Note atau None kalau tidak ditemukan.
    """
    row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    return _row_to_note(row) if row else None


def update_note(conn: sqlite3.Connection, note: Note) -> Note | None:
    """Update metadata note yang sudah ada.

    Args:
        conn: koneksi SQLite.
        note: instance Note dengan id terisi.

    Returns:
        Note yang sudah di-update, atau None kalau id tidak ditemukan.
    """
    conn.execute(
        """UPDATE notes
           SET title = ?, file_path = ?, tags = ?, folder = ?,
               updated_at = strftime('%Y-%m-%dT%H:%M:%S','now')
         WHERE id = ?""",
        (note.title, note.file_path, json.dumps(note.tags), note.folder, note.id),
    )
    conn.commit()
    return get_note(conn, note.id)  # type: ignore[arg-type]


def delete_note(conn: sqlite3.Connection, note_id: int) -> bool:
    """Hapus note berdasarkan ID.

    Args:
        conn: koneksi SQLite.
        note_id: primary key.

    Returns:
        True kalau berhasil dihapus, False kalau tidak ditemukan.
    """
    cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    return cur.rowcount > 0
