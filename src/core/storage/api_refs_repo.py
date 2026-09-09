"""Repository CRUD untuk entity ApiRef.

Catatan keamanan: nilai secret API key TIDAK disimpan di SQLite.
Field ``keychain_key_name`` hanya menyimpan *nama* key di macOS Keychain.
Lihat .agents/rules/security-and-data.md.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from src.core.models import ApiRef


def _row_to_api_ref(row: sqlite3.Row) -> ApiRef:
    """Konversi sqlite3.Row menjadi dataclass ApiRef."""
    return ApiRef(
        id=row["id"],
        service_name=row["service_name"],
        base_url=row["base_url"],
        description=row["description"],
        auth_type=row["auth_type"],
        keychain_key_name=row["keychain_key_name"],
        tags=json.loads(row["tags"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def create_api_ref(conn: sqlite3.Connection, ref: ApiRef) -> ApiRef:
    """Simpan API reference baru ke DB.

    Args:
        conn: koneksi SQLite.
        ref: instance ApiRef (id boleh None).

    Returns:
        ApiRef dengan id yang sudah terisi.
    """
    cur = conn.execute(
        """INSERT INTO api_refs
           (service_name, base_url, description, auth_type, keychain_key_name, tags)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            ref.service_name,
            ref.base_url,
            ref.description,
            ref.auth_type,
            ref.keychain_key_name,
            json.dumps(ref.tags),
        ),
    )
    conn.commit()
    return _row_to_api_ref(
        conn.execute("SELECT * FROM api_refs WHERE id = ?", (cur.lastrowid,)).fetchone()
    )


def list_api_refs(conn: sqlite3.Connection) -> list[ApiRef]:
    """Ambil semua API reference, urut terbaru dulu.

    Args:
        conn: koneksi SQLite.

    Returns:
        Daftar ApiRef.
    """
    rows = conn.execute("SELECT * FROM api_refs ORDER BY updated_at DESC").fetchall()
    return [_row_to_api_ref(r) for r in rows]


def get_api_ref(conn: sqlite3.Connection, ref_id: int) -> ApiRef | None:
    """Ambil satu API reference berdasarkan ID.

    Args:
        conn: koneksi SQLite.
        ref_id: primary key.

    Returns:
        ApiRef atau None kalau tidak ditemukan.
    """
    row = conn.execute("SELECT * FROM api_refs WHERE id = ?", (ref_id,)).fetchone()
    return _row_to_api_ref(row) if row else None


def update_api_ref(conn: sqlite3.Connection, ref: ApiRef) -> ApiRef | None:
    """Update API reference yang sudah ada.

    Args:
        conn: koneksi SQLite.
        ref: instance ApiRef dengan id terisi.

    Returns:
        ApiRef yang sudah di-update, atau None kalau id tidak ditemukan.
    """
    conn.execute(
        """UPDATE api_refs
           SET service_name = ?, base_url = ?, description = ?,
               auth_type = ?, keychain_key_name = ?, tags = ?,
               updated_at = strftime('%Y-%m-%dT%H:%M:%S','now')
         WHERE id = ?""",
        (
            ref.service_name,
            ref.base_url,
            ref.description,
            ref.auth_type,
            ref.keychain_key_name,
            json.dumps(ref.tags),
            ref.id,
        ),
    )
    conn.commit()
    return get_api_ref(conn, ref.id)  # type: ignore[arg-type]


def delete_api_ref(conn: sqlite3.Connection, ref_id: int) -> bool:
    """Hapus API reference berdasarkan ID.

    Args:
        conn: koneksi SQLite.
        ref_id: primary key.

    Returns:
        True kalau berhasil dihapus, False kalau tidak ditemukan.
    """
    cur = conn.execute("DELETE FROM api_refs WHERE id = ?", (ref_id,))
    conn.commit()
    return cur.rowcount > 0
