"""Export & Import data DevCodex ke/from JSON."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from src.core.models import ApiRef, Command, Label, Prompt
from src.core.storage import (
    api_refs_repo,
    commands_repo,
    labels_repo,
    prompts_repo,
)

EXPORT_VERSION = "1.7"


def export_label_to_json(
    conn: sqlite3.Connection, file_path: Path, label_id: int
) -> str:
    """Export data untuk satu label ke file JSON.

    Args:
        conn: koneksi SQLite.
        file_path: path ke file output.
        label_id: ID label yang akan diexport.

    Returns:
        Nama label yang diexport.
    """
    label = labels_repo.get_label(conn, label_id)
    if not label:
        raise ValueError(f"Label dengan ID {label_id} tidak ditemukan")

    # Ambil items yang terkait dengan label ini
    prompt_ids = labels_repo.get_items_by_label(conn, label_id, "prompts")
    cmd_ids = labels_repo.get_items_by_label(conn, label_id, "commands")
    api_ids = labels_repo.get_items_by_label(conn, label_id, "api_refs")

    prompts_data: list[dict[str, Any]] = []
    for pid in prompt_ids:
        p = prompts_repo.get_prompt(conn, pid)
        if p:
            prompts_data.append({
                "title": p.title,
                "content": p.content,
                "tool": p.tool,
                "is_favorite": p.is_favorite,
            })

    commands_data: list[dict[str, Any]] = []
    for cid in cmd_ids:
        c = commands_repo.get_command(conn, cid)
        if c:
            commands_data.append({
                "title": c.title,
                "command_text": c.command_text,
                "description": c.description,
            })

    api_refs_data: list[dict[str, Any]] = []
    for rid in api_ids:
        r = api_refs_repo.get_api_ref(conn, rid)
        if r:
            api_refs_data.append({
                "service_name": r.service_name,
                "base_url": r.base_url,
                "description": r.description,
                "auth_type": r.auth_type,
            })

    data = {
        "version": EXPORT_VERSION,
        "exported_at": datetime.now().isoformat(),
        "label": {
            "name": label.name,
            "color": label.color,
            "description": label.description,
        },
        "prompts": prompts_data,
        "commands": commands_data,
        "api_refs": api_refs_data,
    }

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return label.name


def import_label_from_json(
    conn: sqlite3.Connection, file_path: Path
) -> dict[str, int]:
    """Import data dari file JSON per-label.

    Args:
        conn: koneksi SQLite.
        file_path: path ke file input.

    Returns:
        Dict dengan jumlah item yang diimport per modul.
    """
    raw = json.loads(file_path.read_text())
    counts = {"prompts": 0, "commands": 0, "api_refs": 0}

    # Buat atau dapatkan label
    label_info = raw.get("label", {})
    label_name = label_info.get("name", "Imported")
    existing = labels_repo.list_labels(conn)
    label = None
    for lb in existing:
        if lb.name == label_name:
            label = lb
            break

    if not label:
        label = labels_repo.create_label(
            conn,
            Label(
                id=None,
                name=label_name,
                color=label_info.get("color", "#6C8CFF"),
                description=label_info.get("description", ""),
            ),
        )

    assert label.id is not None

    # Import prompts
    for item in raw.get("prompts", []):
        p = prompts_repo.create_prompt(
            conn,
            Prompt(
                id=None,
                title=item["title"],
                content=item.get("content", ""),
                tool=item.get("tool", ""),
                is_favorite=item.get("is_favorite", False),
            ),
        )
        if p.id is not None:
            labels_repo.set_item_labels(conn, "prompts", p.id, [label.id])
        counts["prompts"] += 1

    # Import commands
    for item in raw.get("commands", []):
        c = commands_repo.create_command(
            conn,
            Command(
                id=None,
                title=item["title"],
                command_text=item.get("command_text", ""),
                description=item.get("description", ""),
            ),
        )
        if c.id is not None:
            labels_repo.set_item_labels(conn, "commands", c.id, [label.id])
        counts["commands"] += 1

    # Import API refs (TANPA keychain secret)
    for item in raw.get("api_refs", []):
        r = api_refs_repo.create_api_ref(
            conn,
            ApiRef(
                id=None,
                service_name=item["service_name"],
                base_url=item.get("base_url", ""),
                description=item.get("description", ""),
                auth_type=item.get("auth_type", ""),
            ),
        )
        if r.id is not None:
            labels_repo.set_item_labels(conn, "api_refs", r.id, [label.id])
        counts["api_refs"] += 1

    return counts
