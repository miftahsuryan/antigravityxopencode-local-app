"""View modul Prompts."""

from __future__ import annotations

import sqlite3
from typing import Any

import flet as ft

from src.app.components.cards import (
    action_button,
    build_label_checkboxes,
    get_selected_label_ids,
    render_label_chips,
)
from src.app.components.markdown_view import render_markdown
from src.app.theme import PALETTE
from src.app.utils.clipboard import copy_to_clipboard
from src.app.views.base import BaseView
from src.core.models import Prompt
from src.core.storage import labels_repo, prompts_repo


class PromptsView(BaseView):
    """View untuk CRUD prompt AI."""

    def __init__(self, page: ft.Page, conn: sqlite3.Connection) -> None:
        super().__init__(
            page, "Prompts", ft.Icons.AUTO_AWESOME_OUTLINED, self._open_add
        )
        self.conn = conn
        self.refresh()

    def _open_add(self) -> None:
        self._open_dialog(None)

    def _open_edit(self, prompt: Prompt) -> None:
        self._open_dialog(prompt)

    def _duplicate(self, prompt: Prompt) -> None:
        prompts_repo.create_prompt(
            self.conn,
            Prompt(
                id=None,
                title=f"{prompt.title} (copy)",
                content=prompt.content,
                tool=prompt.tool,
                label_ids=list(prompt.label_ids),
            ),
        )
        self.refresh()

    def _open_dialog(self, prompt: Prompt | None) -> None:
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

        all_labels = labels_repo.list_labels(self.conn)
        current_label_ids = prompt.label_ids if prompt else []
        label_checks, label_section = build_label_checkboxes(
            all_labels, current_label_ids
        )

        def _save(e: Any) -> None:
            selected_ids = get_selected_label_ids(label_checks)
            if is_edit and prompt:
                prompt.title = (title_field.value or "").strip()
                prompt.content = content_field.value or ""
                prompt.tool = (tool_field.value or "").strip()
                prompt.label_ids = selected_ids
                prompts_repo.update_prompt(self.conn, prompt)
            else:
                prompts_repo.create_prompt(
                    self.conn,
                    Prompt(
                        id=None,
                        title=(title_field.value or "").strip(),
                        content=content_field.value or "",
                        tool=(tool_field.value or "").strip(),
                        label_ids=selected_ids,
                    ),
                )
            self.page.pop_dialog()
            self.refresh()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Prompt" if is_edit else "Tambah Prompt"),
            content=ft.Column(
                [title_field, tool_field, content_field, label_section],
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
        prompt.is_favorite = not prompt.is_favorite
        prompts_repo.update_prompt(self.conn, prompt)
        self.refresh()

    def _delete(self, prompt: Prompt) -> None:
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

    def refresh(self) -> None:
        prompts = prompts_repo.list_prompts(self.conn)
        prompts = self.sort_items(prompts, "title")
        self.list_area.controls.clear()

        if not prompts:
            self.list_area.controls.append(
                self.empty_state("Belum ada prompt. Tambahkan yang pertama!")
            )
        else:
            for p in prompts:
                self.list_area.controls.append(self._item_card(p))
        self.page.update()

    def _item_card(self, prompt: Prompt) -> ft.Container:
        star_color = (
            PALETTE["state.warning"]
            if prompt.is_favorite
            else PALETTE["text.secondary"]
        )
        labels = labels_repo.get_labels_for_item(self.conn, "prompts", prompt.id)  # type: ignore[arg-type]

        # Content preview (truncated)
        content_preview = ft.Text(
            (prompt.content or "")[:120]
            + ("…" if prompt.content and len(prompt.content) > 120 else ""),
            size=12,
            color=PALETTE["text.secondary"],
            max_lines=2,
        )

        # Markdown preview (hidden by default)
        md_preview = ft.Container(
            content=render_markdown(prompt.content or ""),
            visible=False,
        )

        def _toggle_preview(e: ft.ControlEvent) -> None:
            md_preview.visible = not md_preview.visible
            content_preview.visible = not md_preview.visible
            e.control.icon_color = (  # type: ignore[attr-defined]
                PALETTE["accent.primary"] if md_preview.visible
                else PALETTE["text.secondary"]
            )
            e.control.update()

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
                            ft.IconButton(
                                icon=ft.Icons.PREVIEW,
                                icon_color=PALETTE["text.secondary"],
                                tooltip="Preview Markdown",
                                on_click=_toggle_preview,  # type: ignore[arg-type]
                            ),
                            action_button(
                                ft.Icons.COPY_ALL_OUTLINED,
                                "Duplicate",
                                lambda e, p=prompt: self._duplicate(p),
                            ),
                            action_button(
                                ft.Icons.EDIT_OUTLINED,
                                "Edit",
                                lambda e, p=prompt: self._open_edit(p),
                            ),
                            action_button(
                                ft.Icons.DELETE_OUTLINE,
                                "Hapus",
                                lambda e, p=prompt: self._delete(p),
                                danger=True,
                            ),
                        ],
                        spacing=4,
                    ),
                    render_label_chips(labels),
                    content_preview,
                    md_preview,
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
                ],
                spacing=4,
            ),
            bgcolor=PALETTE["bg.surface"],
            border=ft.Border.all(1, PALETTE["border.subtle"]),
            border_radius=8,
            padding=12,
            on_hover=lambda e: _hover_card(e),
        )

    def _copy(self, prompt: Prompt) -> None:
        copy_to_clipboard(
            self.page, prompt.content, f'Prompt "{prompt.title}" disalin.'
        )


def _hover_card(e: ft.ControlEvent) -> None:
    """Efek hover pada kartu."""
    ctrl = e.control
    if e.data == "true":
        ctrl.bgcolor = PALETTE["bg.surface-hover"]  # type: ignore[attr-defined]
        ctrl.update()
    else:
        ctrl.bgcolor = PALETTE["bg.surface"]  # type: ignore[attr-defined]
        ctrl.update()
