"""Search global lintas modul inti."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass
class SearchResult:
    module: str
    item_id: int
    title: str
    snippet: str


def search_all(
    conn: sqlite3.Connection, query: str, limit: int = 50
) -> list[SearchResult]:
    if not query or not query.strip():
        return []

    pattern = f"%{query.strip()}%"
    results: list[SearchResult] = []

    # Labels
    rows = conn.execute(
        """SELECT id, name, description FROM labels
           WHERE name LIKE ? OR description LIKE ?
           ORDER BY updated_at DESC LIMIT ?""",
        (pattern, pattern, limit),
    ).fetchall()
    for r in rows:
        results.append(
            SearchResult(
                module="labels",
                item_id=r["id"],
                title=r["name"],
                snippet=r["description"][:80] if r["description"] else "",
            )
        )

    # Prompts
    rows = conn.execute(
        """SELECT p.id, p.title, p.content FROM prompts p
           WHERE p.title LIKE ? OR p.content LIKE ?
           OR p.tool LIKE ?
           ORDER BY p.updated_at DESC LIMIT ?""",
        (pattern, pattern, pattern, limit),
    ).fetchall()
    for r in rows:
        results.append(
            SearchResult(
                module="prompts",
                item_id=r["id"],
                title=r["title"],
                snippet=(r["content"] or "")[:80],
            )
        )

    # Commands
    rows = conn.execute(
        """SELECT id, title, command_text FROM commands
           WHERE title LIKE ? OR command_text LIKE ?
           OR description LIKE ?
           ORDER BY updated_at DESC LIMIT ?""",
        (pattern, pattern, pattern, limit),
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
           WHERE service_name LIKE ? OR base_url LIKE ?
           OR description LIKE ?
           ORDER BY updated_at DESC LIMIT ?""",
        (pattern, pattern, pattern, limit),
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
