"""Contoh test dasar — ganti/lengkapi mengikuti skill tdd-workflow."""

from src.core.models import Note


def test_note_default_tags_is_empty_list() -> None:
    note = Note(id=None, title="Contoh", file_path="notes/contoh.md")
    assert note.tags == []
