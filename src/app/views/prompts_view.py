"""View modul Prompts.

List prompt AI + form modal tambah/edit + toggle favorit + quick-copy.
"""

from __future__ import annotations

import sqlite3
from typing import Any

import flet as ft

from src.app.theme import PALETTE
from src.app.views.base import BaseView
from src.core.models import Prompt
from src.core.storage import prompts_repo


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
            if is_edit and prompt:
                prompt.title = (title_field.value or "").strip()
                prompt.content = content_field.value or ""
                prompt.tool = (tool_field.value or "").strip()
                prompt.tags = tags
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
                    ),
                )
            self.page.pop_dialog()
            self.refresh()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Prompt" if is_edit else "Tambah Prompt"),
            content=ft.Column(
                [title_field, content_field, tool_field, tags_field],
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
            ft.Container(
                content=ft.Text(t, size=11, color=PALETTE["text.secondary"]),
                bgcolor=PALETTE["bg.surface-hover"],
                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                border_radius=8,
            )
            for t in prompt.tags
        ]
        star_color = (
            PALETTE["state.warning"]
            if prompt.is_favorite
            else PALETTE["text.secondary"]
        )
        return ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.STAR,
                        icon_color=star_color,
                        tooltip="Favorit",
                        on_click=lambda e, p=prompt: self._toggle_favorite(p),
                    ),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        prompt.title,
                                        size=16,
                                        weight=ft.FontWeight.W_600,
                                        color=PALETTE["text.primary"],
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            prompt.tool,
                                            size=11,
                                            color=PALETTE["accent.mint"],
                                        ),
                                        bgcolor=PALETTE["bg.surface-hover"],
                                        padding=ft.Padding.symmetric(
                                            horizontal=6, vertical=2
                                        ),
                                        border_radius=6,
                                    ),
                                ],
                                spacing=6,
                            ),
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
                            (
                                ft.Row(tag_chips, spacing=4)
                                if tag_chips
                                else ft.Container()
                            ),
                        ],
                        spacing=4,
                        expand=True,
                    ),
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
                spacing=8,
            ),
            bgcolor=PALETTE["bg.surface"],
            border=ft.Border.all(1, PALETTE["border.subtle"]),
            border_radius=8,
            padding=12,
        )

    async def _copy(self, prompt: Prompt) -> None:
        """Salin isi prompt ke clipboard & tampilkan snackbar.

        Args:
            prompt: Prompt yang disalin.
        """
        from src.app.utils.clipboard import copy_to_clipboard

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
