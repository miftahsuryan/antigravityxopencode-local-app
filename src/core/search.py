"""Search global lintas 4 modul inti.

Implementasi awal menggunakan LIKE-based query.
Bisa di-upgrade ke FTS5 kalau data sudah besar.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass
class SearchResult:
    """Satu baris hasil search global."""

    module: str  # "notes" | "prompts" | "commands" | "api_refs"
    item_id: int
    title: str
    snippet: str


def search_all(
    conn: sqlite3.Connection, query: str, limit: int = 50
) -> list[SearchResult]:
    """Cari di semua tabel berdasarkan keyword (LIKE).

    Args:
        conn: koneksi SQLite.
        query: kata kunci pencarian.
        limit: jumlah maksimum hasil per modul.

    Returns:
        Daftar SearchResult gabungan dari semua modul, diurutkan per modul.
    """
    if not query or not query.strip():
        return []

    pattern = f"%{query.strip()}%"
    results: list[SearchResult] = []

    # Notes
    rows = conn.execute(
        """SELECT id, title, file_path, content FROM notes
           WHERE title LIKE ? OR tags LIKE ? OR folder LIKE ? OR content LIKE ?
           ORDER BY updated_at DESC LIMIT ?""",
        (pattern, pattern, pattern, pattern, limit),
    ).fetchall()
    for r in rows:
        # Show content preview if title matches file_path
        snippet = r["content"][:80] + "..." if len(r["content"]) > 80 else r["content"]
        results.append(
            SearchResult(
                module="notes",
                item_id=r["id"],
                title=r["title"],
                snippet=snippet,
            )
        )

    # Prompts
    rows = conn.execute(
        """SELECT id, title, content FROM prompts
           WHERE title LIKE ? OR content LIKE ? OR tool LIKE ? OR tags LIKE ?
           ORDER BY updated_at DESC LIMIT ?""",
        (pattern, pattern, pattern, pattern, limit),
    ).fetchall()
    for r in rows:
        content_preview = (r["content"] or "")[:80]
        results.append(
            SearchResult(
                module="prompts",
                item_id=r["id"],
                title=r["title"],
                snippet=content_preview,
            )
        )

    # Commands
    rows = conn.execute(
        """SELECT id, title, command_text FROM commands
           WHERE title LIKE ? OR command_text LIKE ? OR description LIKE ?
                 OR tags LIKE ?
           ORDER BY updated_at DESC LIMIT ?""",
        (pattern, pattern, pattern, pattern, limit),
    ).fetchall()
    for r in rows:
        results.append(
            SearchResult(
                module="commands",
                item_id=r["id"],
                title=r["title"],
                snippet=r["command_text"],
            )
        )

    # API References
    rows = conn.execute(
        """SELECT id, service_name, base_url FROM api_refs
           WHERE service_name LIKE ? OR base_url LIKE ? OR description LIKE ?
                 OR tags LIKE ?
           ORDER BY updated_at DESC LIMIT ?""",
        (pattern, pattern, pattern, pattern, limit),
    ).fetchall()
    for r in rows:
        results.append(
            SearchResult(
                module="api_refs",
                item_id=r["id"],
                title=r["service_name"],
                snippet=r["base_url"],
            )
        )

    return results
