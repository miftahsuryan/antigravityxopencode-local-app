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

EXPORT_VERSION = "1.6"


def export_to_json(conn: sqlite3.Connection, file_path: Path) -> None:
    """Export semua data ke file JSON."""
    labels_data: list[dict[str, str]] = []
    prompts_data: list[dict[str, Any]] = []
    commands_data: list[dict[str, Any]] = []
    api_refs_data: list[dict[str, Any]] = []

    for label in labels_repo.list_labels(conn):
        labels_data.append({
            "name": label.name,
            "color": label.color,
            "description": label.description,
        })

    for prompt in prompts_repo.list_prompts(conn):
        pid = prompt.id if prompt.id is not None else 0
        labels = labels_repo.get_labels_for_item(conn, "prompts", pid)
        prompts_data.append({
            "title": prompt.title,
            "content": prompt.content,
            "tool": prompt.tool,
            "is_favorite": prompt.is_favorite,
            "label_names": [lb.name for lb in labels],
        })

    for cmd in commands_repo.list_commands(conn):
        cid = cmd.id if cmd.id is not None else 0
        labels = labels_repo.get_labels_for_item(conn, "commands", cid)
        commands_data.append({
            "title": cmd.title,
            "command_text": cmd.command_text,
            "description": cmd.description,
            "label_names": [lb.name for lb in labels],
        })

    for ref in api_refs_repo.list_api_refs(conn):
        rid = ref.id if ref.id is not None else 0
        labels = labels_repo.get_labels_for_item(conn, "api_refs", rid)
        api_refs_data.append({
            "service_name": ref.service_name,
            "base_url": ref.base_url,
            "description": ref.description,
            "auth_type": ref.auth_type,
            "keychain_key_name": ref.keychain_key_name,
            "label_names": [lb.name for lb in labels],
        })

    data = {
        "version": EXPORT_VERSION,
        "exported_at": datetime.now().isoformat(),
        "labels": labels_data,
        "prompts": prompts_data,
        "commands": commands_data,
        "api_refs": api_refs_data,
    }

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def import_from_json(
    conn: sqlite3.Connection, file_path: Path, merge: bool = True
) -> dict[str, int]:
    """Import data dari file JSON.

    Args:
        conn: koneksi SQLite.
        file_path: path ke file input.
        merge: True = skip duplikat, False = clear semua lalu import.

    Returns:
        Dict dengan jumlah item yang diimport per modul.
    """
    raw = json.loads(file_path.read_text())
    counts = {"labels": 0, "prompts": 0, "commands": 0, "api_refs": 0}

    if not merge:
        _clear_all(conn)

    # Import labels first (butuh ID untuk mapping)
    label_map: dict[str, int] = {}
    existing_labels = {lb.name: lb for lb in labels_repo.list_labels(conn)}

    for item in raw.get("labels", []):
        name = item["name"]
        if merge and name in existing_labels:
            lid = existing_labels[name].id
            if lid is not None:
                label_map[name] = lid
            continue
        label = labels_repo.create_label(
            conn,
            Label(
                id=None,
                name=name,
                color=item.get("color", "#6C8CFF"),
                description=item.get("description", ""),
            ),
        )
        if label.id is not None:
            label_map[name] = label.id
        counts["labels"] += 1

    # Re-fetch after creating new labels
    if not merge:
        for lb in labels_repo.list_labels(conn):
            if lb.id is not None:
                label_map[lb.name] = lb.id

    # Import prompts
    for item in raw.get("prompts", []):
        label_ids = [
            label_map[name]
            for name in item.get("label_names", [])
            if name in label_map
        ]
        prompts_repo.create_prompt(
            conn,
            Prompt(
                id=None,
                title=item["title"],
                content=item.get("content", ""),
                tool=item.get("tool", ""),
                is_favorite=item.get("is_favorite", False),
                label_ids=label_ids,
            ),
        )
        counts["prompts"] += 1

    # Import commands
    for item in raw.get("commands", []):
        label_ids = [
            label_map[name]
            for name in item.get("label_names", [])
            if name in label_map
        ]
        commands_repo.create_command(
            conn,
            Command(
                id=None,
                title=item["title"],
                command_text=item.get("command_text", ""),
                description=item.get("description", ""),
                label_ids=label_ids,
            ),
        )
        counts["commands"] += 1

    # Import API refs (TANPA keychain secret — secret harus diimpor manual)
    for item in raw.get("api_refs", []):
        label_ids = [
            label_map[name]
            for name in item.get("label_names", [])
            if name in label_map
        ]
        api_refs_repo.create_api_ref(
            conn,
            ApiRef(
                id=None,
                service_name=item["service_name"],
                base_url=item.get("base_url", ""),
                description=item.get("description", ""),
                auth_type=item.get("auth_type", ""),
                keychain_key_name=item.get("keychain_key_name", ""),
                label_ids=label_ids,
            ),
        )
        counts["api_refs"] += 1

    return counts


def _clear_all(conn: sqlite3.Connection) -> None:
    """Hapus semua data dari semua tabel."""
    conn.execute("DELETE FROM label_items")
    conn.execute("DELETE FROM prompts")
    conn.execute("DELETE FROM commands")
    conn.execute("DELETE FROM api_refs")
    conn.execute("DELETE FROM labels")
    conn.commit()
