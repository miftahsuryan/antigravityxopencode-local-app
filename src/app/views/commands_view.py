"""View modul Commands.

List command terminal + form modal tambah/edit + quick-copy.
Hanya menyimpan teks — tidak mengeksekusi apa pun (lihat aturan keamanan).
"""

from __future__ import annotations

import sqlite3
from typing import Any

import flet as ft

from src.app.theme import PALETTE
from src.app.utils.clipboard import copy_to_clipboard
from src.app.views.base import BaseView
from src.core.models import Command
from src.core.storage import commands_repo, projects_repo


class CommandsView(BaseView):
    """View untuk CRUD command snippets."""

    def __init__(self, page: ft.Page, conn: sqlite3.Connection) -> None:
        """Inisialisasi view Commands.

        Args:
            page: objek Page Flet.
            conn: koneksi SQLite yang sudah siap.
        """
        super().__init__(page, "Commands", ft.Icons.TERMINAL_OUTLINED, self._open_add)
        self.conn = conn
        self._current_filter_tag: str | None = None
        self.refresh()

    # ------------------------------------------------------------------
    # Form & dialog
    # ------------------------------------------------------------------

    def _open_add(self) -> None:
        """Buka dialog form tambah command baru."""
        self._open_dialog(None)

    def _open_edit(self, cmd: Command) -> None:
        """Buka dialog form edit command.

        Args:
            cmd: Command yang akan diedit.
        """
        self._open_dialog(cmd)

    def _open_dialog(self, cmd: Command | None) -> None:
        """Tampilkan modal form tambah/edit.

        Args:
            cmd: Command untuk mode edit, atau None untuk mode tambah.
        """
        is_edit = cmd is not None
        title_field = ft.TextField(
            label="Judul", value=cmd.title if cmd else "", dense=True
        )
        command_field = ft.TextField(
            label="Command",
            value=cmd.command_text if cmd else "",
            dense=True,
            text_style=ft.TextStyle(font_family="monospace"),
        )
        desc_field = ft.TextField(
            label="Deskripsi",
            value=cmd.description if cmd else "",
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        tags_field = ft.TextField(
            label="Tags (pisahkan dengan koma)",
            value=", ".join(cmd.tags) if cmd else "",
            dense=True,
        )

        def _save(e: Any) -> None:
            tags = [t.strip() for t in (tags_field.value or "").split(",") if t.strip()]
            pid: int | None = None
            raw_pid = project_field.value if project_field else None
            if raw_pid and raw_pid != "":
                try:
                    pid = int(raw_pid)
                except ValueError:
                    pid = None
            if is_edit and cmd:
                cmd.title = (title_field.value or "").strip()
                cmd.command_text = (command_field.value or "").strip()
                cmd.description = desc_field.value or ""
                cmd.tags = tags
                cmd.project_id = pid
                commands_repo.update_command(self.conn, cmd)
            else:
                commands_repo.create_command(
                    self.conn,
                    Command(
                        id=None,
                        title=(title_field.value or "").strip(),
                        command_text=(command_field.value or "").strip(),
                        description=desc_field.value or "",
                        tags=tags,
                        project_id=pid,
                    ),
                )
            self.page.pop_dialog()
            self.refresh()

        project_options = [ft.dropdown.Option("")]
        projects = projects_repo.list_projects(self.conn)
        for p in projects:
            project_options.append(ft.dropdown.Option(str(p.id), p.name))

        project_field = ft.Dropdown(
            label="Project",
            options=project_options,
            dense=True,
        )
        if is_edit and cmd and cmd.project_id:
            project_field.value = str(cmd.project_id)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Command" if is_edit else "Tambah Command"),
            content=ft.Column(
                [title_field, project_field, command_field, desc_field, tags_field],
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

    def _delete(self, cmd: Command) -> None:
        """Hapus command (dengan konfirmasi).

        Args:
            cmd: Command yang akan dihapus.
        """

        def _confirm(e: Any) -> None:
            commands_repo.delete_command(self.conn, cmd.id)  # type: ignore[arg-type]
            self.page.pop_dialog()
            self.refresh()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Hapus command?"),
            content=ft.Text(f'"{cmd.title}" akan dihapus.'),
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
        """Hapus filter tag dan tampilkan semua command."""
        self._current_filter_tag = None
        self.refresh()

    def _apply_filter(self) -> None:
        """Terapkan filter berdasarkan tag yang sedang aktif."""
        commands = commands_repo.list_commands(self.conn)
        self.list_area.controls.clear()

        if self._current_filter_tag:
            filtered = [c for c in commands if self._current_filter_tag in c.tags]
            if not filtered:
                tag = self._current_filter_tag
                msg = f"Tidak ada command dengan tag '{tag}'"
                self.list_area.controls.append(self.empty_state(msg))
            else:
                for c in filtered:
                    self.list_area.controls.append(self._item_card(c))
        else:
            if not commands:
                self.list_area.controls.append(
                    self.empty_state("Belum ada command. Tambahkan yang pertama!")
                )
            else:
                for c in commands:
                    self.list_area.controls.append(self._item_card(c))
        self.page.update()

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Perbarui daftar command di area list."""
        commands = commands_repo.list_commands(self.conn)
        self.list_area.controls.clear()

        if not commands:
            self.list_area.controls.append(
                self.empty_state("Belum ada command. Tambahkan yang pertama!")
            )
        else:
            for c in commands:
                self.list_area.controls.append(self._item_card(c))
        self.page.update()

    def _item_card(self, cmd: Command) -> ft.Container:
        """Render satu kartu command.

        Args:
            cmd: Command yang dirender.

        Returns:
            Container kartu command.
        """
        tag_chips: list[ft.Control] = [
            self._tag_chip(t) for t in cmd.tags
        ]
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                cmd.title,
                                size=16,
                                weight=ft.FontWeight.W_600,
                                color=PALETTE["text.primary"],
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon=ft.Icons.CONTENT_COPY,
                                icon_color=PALETTE["text.secondary"],
                                tooltip="Copy",
                                on_click=lambda e, c=cmd: self._copy(c),
                            ),
                            _action_button(
                                ft.Icons.EDIT_OUTLINED,
                                "Edit",
                                lambda e, c=cmd: self._open_edit(c),
                            ),
                            _action_button(
                                ft.Icons.DELETE_OUTLINE,
                                "Hapus",
                                lambda e, c=cmd: self._delete(c),
                                danger=True,
                            ),
                        ],
                        spacing=4,
                    ),
                    ft.Row(tag_chips, spacing=4) if tag_chips else ft.Container(),
                    ft.Container(
                        content=ft.Text(
                            cmd.command_text,
                            size=13,
                            color=PALETTE["accent.mint"],
                            style=ft.TextStyle(font_family="monospace"),
                        ),
                        bgcolor=PALETTE["bg.surface-hover"],
                        padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                        border_radius=6,
                    ),
                    ft.Text(
                        cmd.description or "",
                        size=12,
                        color=PALETTE["text.secondary"],
                        max_lines=2,
                    ),
                ],
                spacing=4,
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

    def _copy(self, cmd: Command) -> None:
        """Salin command ke clipboard & tampilkan snackbar.

        Args:
            cmd: Command yang disalin.
        """
        copy_to_clipboard(
            self.page, cmd.command_text, f'Command "{cmd.title}" disalin.'
        )


def _action_button(
    icon: Any, tooltip: str, on_click: Any, danger: bool = False
) -> ft.IconButton:
    """Buat tombol aksi ikon kecil.

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
