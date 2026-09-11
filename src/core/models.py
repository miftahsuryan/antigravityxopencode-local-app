"""Dataclass model untuk entity inti DevCodex."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Label:
    id: int | None
    name: str
    color: str = "#6C8CFF"
    description: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Prompt:
    id: int | None
    title: str
    content: str
    tool: str = ""
    is_favorite: bool = False
    label_ids: list[int] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Command:
    id: int | None
    title: str
    command_text: str
    description: str = ""
    label_ids: list[int] = field(default_factory=list)
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
    label_ids: list[int] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
