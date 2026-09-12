"""Test dataclass models."""

from __future__ import annotations

from src.core.models import ApiRef, Command, Label, Prompt


def test_label_defaults() -> None:
    label = Label(id=1, name="Test")
    assert label.color == "#6C8CFF"
    assert label.description == ""
    assert label.created_at is None


def test_prompt_defaults() -> None:
    prompt = Prompt(id=1, title="Test", content="Hello")
    assert prompt.tool == ""
    assert prompt.is_favorite is False
    assert prompt.label_ids == []


def test_command_defaults() -> None:
    cmd = Command(id=1, title="Test", command_text="ls -la")
    assert cmd.description == ""
    assert cmd.label_ids == []


def test_api_ref_defaults() -> None:
    ref = ApiRef(id=1, service_name="Test", base_url="https://test.com")
    assert ref.description == ""
    assert ref.auth_type == ""
    assert ref.keychain_key_name == ""
    assert ref.label_ids == []


def test_prompt_label_ids_mutable() -> None:
    prompt = Prompt(id=1, title="Test", content="Hello")
    prompt.label_ids = [1, 2, 3]
    assert prompt.label_ids == [1, 2, 3]
