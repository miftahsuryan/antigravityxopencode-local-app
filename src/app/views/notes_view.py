"""View modul Notes.

List catatan + form modal tambah/edit. Menampilkan title, folder, dan tags.
Konten Markdown asli disimpan di file vault; view ini mengelola metadata/index.
"""

from __future__ import annotations

import sqlite3
from typing import Any

import flet as ft

from src.app.theme import PALETTE
from src.app.utils.clipboard import copy_to_clipboard
from src.app.views.base import BaseView
from src.core.models import Note
from src.core.storage import notes_repo


class NotesView(BaseView):
    """View untuk CRUD catatan."""

    def __init__(self, page: ft.Page, conn: sqlite3.Connection) -> None:
        """Inisialisasi view Notes.

        Args:
            page: objek Page Flet.
            conn: koneksi SQLite yang sudah siap.
        """
        super().__init__(page, "Notes", ft.Icons.DESCRIPTION_OUTLINED, self._open_add)
        self.conn = conn
        self._current_filter_tag: str | None = None
        self.refresh()

    # ------------------------------------------------------------------
    # Form & dialog
    # ------------------------------------------------------------------

    def _open_add(self) -> None:
        """Buka dialog form untuk tambah note baru."""
        self._open_dialog(None)

    def _open_edit(self, note: Note) -> None:
        """Buka dialog form untuk edit note.

        Args:
            note: Note yang akan diedit.
        """
        self._open_dialog(note)

    def _open_dialog(self, note: Note | None) -> None:
        """Tampilkan modal form tambah/edit.

        Args:
            note: Note untuk mode edit, atau None untuk mode tambah.
        """
        is_edit = note is not None
        title_field = ft.TextField(
            label="Judul",
            value=note.title if note else "",
            dense=True,
        )
        path_field = ft.TextField(
            label="File path (vault)",
            value=note.file_path if note else "notes/",
            dense=True,
        )
        folder_field = ft.TextField(
            label="Folder",
            value=note.folder if note else "",
            dense=True,
        )
        tags_field = ft.TextField(
            label="Tags (pisahkan dengan koma)",
            value=", ".join(note.tags) if note else "",
            dense=True,
        )
        content_field = ft.TextField(
            label="Konten Catatan",
            value=note.content if note else "",
            multiline=True,
            min_lines=4,
            max_lines=10,
            text_style=ft.TextStyle(font_family="monospace"),
        )

        def _save(e: Any) -> None:
            tags = [t.strip() for t in (tags_field.value or "").split(",") if t.strip()]
            if is_edit and note:
                note.title = (title_field.value or "").strip()
                note.file_path = (path_field.value or "").strip()
                note.folder = (folder_field.value or "").strip()
                note.tags = tags
                note.content = content_field.value or ""
                notes_repo.update_note(self.conn, note)
            else:
                notes_repo.create_note(
                    self.conn,
                    Note(
                        id=None,
                        title=(title_field.value or "").strip(),
                        file_path=(path_field.value or "").strip(),
                        folder=(folder_field.value or "").strip(),
                        tags=tags,
                        content=content_field.value or "",
                    ),
                )
            self.page.pop_dialog()
            self.refresh()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Note" if is_edit else "Tambah Note"),
            content=ft.Column(
                [
                    title_field,
                    path_field,
                    folder_field,
                    tags_field,
                    ft.Text("Konten:", size=12, color=PALETTE["text.secondary"]),
                    content_field,
                ],
                spacing=8,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton("Batal", on_click=lambda e: self.page.pop_dialog()),
                ft.FilledButton("Simpan", on_click=_save),
            ],
        )
        self.page.show_dialog(dialog)

    def _copy(self, note: Note) -> None:
        """Salin konten note ke clipboard & tampilkan snackbar.

        Args:
            note: Note yang disalin.
        """
        copy_to_clipboard(self.page, note.content, f'Catatan "{note.title}" disalin.')

    def _delete(self, note: Note) -> None:
        """Hapus note (dengan konfirmasi).

        Args:
            note: Note yang akan dihapus.
        """

        def _confirm(e: Any) -> None:
            notes_repo.delete_note(self.conn, note.id)  # type: ignore[arg-type]
            self.page.pop_dialog()
            self.refresh()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Hapus note?"),
            content=ft.Text(f'"{note.title}" akan dihapus.'),
            actions=[
                ft.TextButton("Batal", on_click=lambda e: self.page.pop_dialog()),
                ft.FilledButton(
                    "Hapus",
                    bgcolor=PALETTE["state.danger"],
                    on_click=_confirm,
                ),
            ],
        )
        self.page.show_dialog(dialog)

    # ------------------------------------------------------------------
    # Filter & tag
    # ------------------------------------------------------------------

    def _chip_click(self, tag: str) -> None:
        """Toggle filter by tag saat tag chip diklik.

        Args:
            tag: Tag yang diklik.
        """
        if self._current_filter_tag == tag:
            self._current_filter_tag = None
        else:
            self._current_filter_tag = tag
        self._apply_filter()

    def _clear_filter(self) -> None:
        """Hapus filter tag dan tampilkan semua note."""
        self._current_filter_tag = None
        self.refresh()

    def _apply_filter(self) -> None:
        """Terapkan filter berdasarkan tag yang sedang aktif."""
        notes = notes_repo.list_notes(self.conn)
        self.list_area.controls.clear()

        if self._current_filter_tag:
            filtered = [n for n in notes if self._current_filter_tag in n.tags]
            if not filtered:
                tag = self._current_filter_tag
                msg = f"Tidak ada catatan dengan tag '{tag}'"
                self.list_area.controls.append(self.empty_state(msg))
            else:
                for note in filtered:
                    self.list_area.controls.append(self._item_card(note))
        else:
            if not notes:
                self.list_area.controls.append(
                    self.empty_state("Belum ada catatan. Tambahkan yang pertama!")
                )
            else:
                for note in notes:
                    self.list_area.controls.append(self._item_card(note))
        self.page.update()

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Perbarui daftar note di area list."""
        notes = notes_repo.list_notes(self.conn)
        self.list_area.controls.clear()

        if not notes:
            self.list_area.controls.append(
                self.empty_state("Belum ada catatan. Tambahkan yang pertama!")
            )
        else:
            for note in notes:
                self.list_area.controls.append(self._item_card(note))
        self.page.update()

    def _item_card(self, note: Note) -> ft.Container:
        """Render satu kartu note.

        Args:
            note: Note yang dirender.

        Returns:
            Container kartu note.
        """
        tag_chips: list[ft.Control] = [
            self._tag_chip(t) for t in note.tags
        ]
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                note.title,
                                size=16,
                                weight=ft.FontWeight.W_600,
                                color=PALETTE["text.primary"],
                            ),
                            ft.Container(expand=True),
                            _action_button(
                                ft.Icons.CONTENT_COPY,
                                "Salin",
                                lambda e, n=note: self._copy(n),
                            ),
                            _action_button(
                                ft.Icons.EDIT_OUTLINED,
                                "Edit",
                                lambda e, n=note: self._open_edit(n),
                            ),
                            _action_button(
                                ft.Icons.DELETE_OUTLINE,
                                "Hapus",
                                lambda e, n=note: self._delete(n),
                                danger=True,
                            ),
                        ],
                        spacing=4,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Row(tag_chips, spacing=4) if tag_chips else ft.Container(),
                    ft.Text(
                        note.content if note.content else "(Tanpa konten)",
                        size=13,
                        color=PALETTE["text.primary"],
                        style=ft.TextStyle(font_family="monospace"),
                        max_lines=8,
                    ),
                    ft.Text(
                        note.folder if note.folder else "Tanpa folder",
                        size=11,
                        color=PALETTE["text.secondary"],
                        style=ft.TextStyle(font_family="monospace"),
                    ),
                ],
                spacing=6,
            ),
            bgcolor=PALETTE["bg.surface"],
            border=ft.Border.all(1, PALETTE["border.subtle"]),
            border_radius=8,
            padding=12,
        )

    def _tag_chip(self, tag: str) -> ft.Container:
        """Buat tag chip yang bisa diklik untuk filter.

        Args:
            tag: Teks tag.

        Returns:
            Container yang bisa diklik.
        """
        is_active = self._current_filter_tag == tag
        accent = PALETTE["accent.primary"]
        surface = PALETTE["bg.surface-hover"]
        base = PALETTE["bg.base"]
        secondary = PALETTE["text.secondary"]
        chip_bg = accent if is_active else surface
        chip_fg = base if is_active else secondary
        return ft.Container(
            content=ft.Text(tag, size=11, color=chip_fg),
            bgcolor=chip_bg,
            padding=ft.Padding.symmetric(horizontal=8, vertical=2),
            border_radius=8,
            on_click=lambda e, t=tag: self._chip_click(t),
            ink=True,
        )


def _action_button(
    icon: Any, tooltip: str, on_click: Any, danger: bool = False
) -> ft.IconButton:
    """Buat tombol aksi ikon kecil (edit/hapus).

    Args:
        icon: ikon Flet.
        tooltip: tooltip tombol.
        on_click: callback saat diklik.
        danger: True untuk style merah.

    Returns:
        IconButton.
    """
    return ft.IconButton(
        icon=icon,
        icon_color=PALETTE["state.danger"] if danger else PALETTE["text.secondary"],
        tooltip=tooltip,
        on_click=on_click,
    )
