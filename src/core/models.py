"""Dataclass model untuk entity inti DevCodex.

Implementasi lengkap dibangun mengikuti
docs/paper-trail/0001-mvp-core-modules.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Note:
    id: int | None
    title: str
    file_path: str
    content: str = ""
    tags: list[str] = field(default_factory=list)
    folder: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Prompt:
    id: int | None
    title: str
    content: str
    tool: str = ""
    tags: list[str] = field(default_factory=list)
    is_favorite: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Command:
    id: int | None
    title: str
    command_text: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class ApiRef:
    id: int | None
    service_name: str
    base_url: str
    description: str = ""
    auth_type: str = ""
    keychain_key_name: str = ""
    tags: list[str] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
