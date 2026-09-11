"""View modul Prompts.

List prompt AI + form modal tambah/edit + toggle favorit + quick-copy.
"""

from __future__ import annotations

import sqlite3
from typing import Any

import flet as ft

from src.app.theme import PALETTE
from src.app.utils.clipboard import copy_to_clipboard
from src.app.views.base import BaseView
from src.core.models import Prompt
from src.core.storage import prompts_repo
from src.core.storage import projects_repo


class PromptsView(BaseView):
    """View untuk CRUD prompt AI."""

    def __init__(self, page: ft.Page, conn: sqlite3.Connection) -> None:
        """Inisialisasi view Prompts.

        Args:
            page: objek Page Flet.
            conn: koneksi SQLite yang sudah siap.
        """
        super().__init__(
            page, "Prompts", ft.Icons.AUTO_AWESOME_OUTLINED, self._open_add
        )
        self.conn = conn
        self._current_filter_tag: str | None = None
        self.refresh()

    # ------------------------------------------------------------------
    # Form & dialog
    # ------------------------------------------------------------------

    def _open_add(self) -> None:
        """Buka dialog form tambah prompt baru."""
        self._open_dialog(None)

    def _open_edit(self, prompt: Prompt) -> None:
        """Buka dialog form edit prompt.

        Args:
            prompt: Prompt yang akan diedit.
        """
        self._open_dialog(prompt)

    def _open_dialog(self, prompt: Prompt | None) -> None:
        """Tampilkan modal form tambah/edit.

        Args:
            prompt: Prompt untuk mode edit, atau None untuk mode tambah.
        """
        is_edit = prompt is not None
        title_field = ft.TextField(
            label="Judul", value=prompt.title if prompt else "", dense=True
        )
        content_field = ft.TextField(
            label="Isi prompt",
            value=prompt.content if prompt else "",
            multiline=True,
            min_lines=4,
            max_lines=8,
        )
        tool_field = ft.TextField(
            label="Tool/Model (mis. claude, gemini)",
            value=prompt.tool if prompt else "",
            dense=True,
        )
        tags_field = ft.TextField(
            label="Tags (pisahkan dengan koma)",
            value=", ".join(prompt.tags) if prompt else "",
            dense=True,
        )

        def _save(e: Any) -> None:
            tags = [t.strip() for t in (tags_field.value or "").split(",") if t.strip()]
            pid = project_field.value if project_field else None
            if pid and pid != "":
                try:
                    pid = int(pid)
                except ValueError:
                    pid = None
            if is_edit and prompt:
                prompt.title = (title_field.value or "").strip()
                prompt.content = content_field.value or ""
                prompt.tool = (tool_field.value or "").strip()
                prompt.tags = tags
                prompt.project_id = pid
                prompts_repo.update_prompt(self.conn, prompt)
            else:
                prompts_repo.create_prompt(
                    self.conn,
                    Prompt(
                        id=None,
                        title=(title_field.value or "").strip(),
                        content=content_field.value or "",
                        tool=(tool_field.value or "").strip(),
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
        if is_edit and prompt and prompt.project_id:
            project_field.value = str(prompt.project_id)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Prompt" if is_edit else "Tambah Prompt"),
            content=ft.Column(
                [title_field, project_field, content_field, tool_field, tags_field],
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

    def _toggle_favorite(self, prompt: Prompt) -> None:
        """Toggle flag favorit prompt.

        Args:
            prompt: Prompt yang di-toggle.
        """
        prompt.is_favorite = not prompt.is_favorite
        prompts_repo.update_prompt(self.conn, prompt)
        self.refresh()

    def _delete(self, prompt: Prompt) -> None:
        """Hapus prompt (dengan konfirmasi).

        Args:
            prompt: Prompt yang akan dihapus.
        """

        def _confirm(e: Any) -> None:
            prompts_repo.delete_prompt(self.conn, prompt.id)  # type: ignore[arg-type]
            self.page.pop_dialog()
            self.refresh()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Hapus prompt?"),
            content=ft.Text(f'"{prompt.title}" akan dihapus.'),
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
        """Hapus filter tag dan tampilkan semua prompt."""
        self._current_filter_tag = None
        self.refresh()

    def _apply_filter(self) -> None:
        """Terapkan filter berdasarkan tag yang sedang aktif."""
        prompts = prompts_repo.list_prompts(self.conn)
        self.list_area.controls.clear()

        if self._current_filter_tag:
            filtered = [p for p in prompts if self._current_filter_tag in p.tags]
            if not filtered:
                tag = self._current_filter_tag
                msg = f"Tidak ada prompt dengan tag '{tag}'"
                self.list_area.controls.append(self.empty_state(msg))
            else:
                for p in filtered:
                    self.list_area.controls.append(self._item_card(p))
        else:
            if not prompts:
                self.list_area.controls.append(
                    self.empty_state("Belum ada prompt. Tambahkan yang pertama!")
                )
            else:
                for p in sorted(
                    prompts, key=lambda x: (not x.is_favorite, x.updated_at or 0)
                ):
                    self.list_area.controls.append(self._item_card(p))
        self.page.update()

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Perbarui daftar prompt di area list."""
        prompts = prompts_repo.list_prompts(self.conn)
        self.list_area.controls.clear()

        if not prompts:
            self.list_area.controls.append(
                self.empty_state("Belum ada prompt. Tambahkan yang pertama!")
            )
        else:
            for p in sorted(
                prompts, key=lambda x: (not x.is_favorite, x.updated_at or 0)
            ):
                self.list_area.controls.append(self._item_card(p))
        self.page.update()

    def _item_card(self, prompt: Prompt) -> ft.Container:
        """Render satu kartu prompt.

        Args:
            prompt: Prompt yang dirender.

        Returns:
            Container kartu prompt.
        """
        tag_chips: list[ft.Control] = [
            self._tag_chip(t) for t in prompt.tags
        ]
        star_color = (
            PALETTE["state.warning"]
            if prompt.is_favorite
            else PALETTE["text.secondary"]
        )
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.STAR,
                                icon_color=star_color,
                                tooltip="Favorit",
                                on_click=lambda e, p=prompt: self._toggle_favorite(p),
                            ),
                            ft.Text(
                                prompt.title,
                                size=16,
                                weight=ft.FontWeight.W_600,
                                color=PALETTE["text.primary"],
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon=ft.Icons.CONTENT_COPY,
                                icon_color=PALETTE["text.secondary"],
                                tooltip="Copy",
                                on_click=lambda e, p=prompt: self._copy(p),
                            ),
                            _action_button(
                                ft.Icons.EDIT_OUTLINED,
                                "Edit",
                                lambda e, p=prompt: self._open_edit(p),
                            ),
                            _action_button(
                                ft.Icons.DELETE_OUTLINE,
                                "Hapus",
                                lambda e, p=prompt: self._delete(p),
                                danger=True,
                            ),
                        ],
                        spacing=4,
                    ),
                    ft.Row(tag_chips, spacing=4) if tag_chips else ft.Container(),
                    ft.Text(
                        (prompt.content or "")[:120]
                        + (
                            "…"
                            if prompt.content and len(prompt.content) > 120
                            else ""
                        ),
                        size=12,
                        color=PALETTE["text.secondary"],
                        max_lines=2,
                    ),
                    ft.Container(
                        content=ft.Text(
                            prompt.tool,
                            size=11,
                            color=PALETTE["accent.mint"],
                        ),
                        bgcolor=PALETTE["bg.surface-hover"],
                        padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                        border_radius=6,
                    ),
                    self._project_badge(prompt),
                ],
                spacing=4,
            ),
            bgcolor=PALETTE["bg.surface"],
            border=ft.Border.all(1, PALETTE["border.subtle"]),
            border_radius=8,
            padding=12,
        )

    def _project_badge(self, prompt: Prompt) -> ft.Container:
        if not prompt.project_id:
            return ft.Container()
        return ft.Container(
            content=ft.Text(
                f"Project {prompt.project_id}",
                size=11,
                color=PALETTE["accent.primary"],
            ),
            bgcolor=PALETTE["bg.surface-hover"],
            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
            border_radius=6,
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

    def _copy(self, prompt: Prompt) -> None:
        """Salin isi prompt ke clipboard & tampilkan snackbar.

        Args:
            prompt: Prompt yang disalin.
        """
        copy_to_clipboard(
            self.page, prompt.content, f'Prompt "{prompt.title}" disalin.'
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
