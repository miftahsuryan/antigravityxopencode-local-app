"""View modul Labels — CRUD label + tampilan tersegmentasi per label.

Label digunakan untuk mengelompokkan prompt, command, dan API key.
Tampilan label menunjukkan item-item yang terkait dengan setiap label.
"""

from __future__ import annotations

import sqlite3
from typing import Any

import flet as ft

from src.app.components.cards import action_button, copy_button, label_chip
from src.app.theme import PALETTE
from src.app.utils.clipboard import copy_to_clipboard
from src.app.views.base import BaseView
from src.core.models import ApiRef, Command, Label, Prompt
from src.core.secrets import get_secret
from src.core.storage import api_refs_repo, commands_repo, labels_repo, prompts_repo

# Daftar warna yang tersedia untuk label.
LABEL_COLORS: list[str] = [
    "#6C8CFF",
    "#2DD4BF",
    "#F5A623",
    "#F5484B",
    "#3DDC84",
    "#E879F9",
    "#FB923C",
    "#60A5FA",
]


class LabelsView(BaseView):
    """View untuk manajemen label dan tampilan tersegmentasi."""

    def __init__(self, page: ft.Page, conn: sqlite3.Connection) -> None:
        super().__init__(page, "Labels", ft.Icons.LABEL_OUTLINED, self._open_add)
        self.conn = conn
        self.refresh()

    # ------------------------------------------------------------------
    # Form & dialog
    # ------------------------------------------------------------------

    def _open_add(self) -> None:
        self._open_dialog(None)

    def _open_edit(self, label: Label) -> None:
        self._open_dialog(label)

    def _open_dialog(self, label: Label | None) -> None:
        is_edit = label is not None
        name_field = ft.TextField(
            label="Nama Label",
            value=label.name if label else "",
            dense=True,
        )
        desc_field = ft.TextField(
            label="Deskripsi",
            value=label.description if label else "",
            dense=True,
        )

        selected_color = label.color if label else LABEL_COLORS[0]

        def _make_color_btn(hex_color: str) -> ft.Container:
            is_sel = selected_color == hex_color
            return ft.Container(
                width=28,
                height=28,
                bgcolor=hex_color,
                border_radius=14,
                border=ft.Border.all(
                    2, PALETTE["text.primary"] if is_sel else PALETTE["bg.base"]
                ),
                on_click=lambda e, c=hex_color: _select_color(c),
            )

        color_row = ft.Row(
            [_make_color_btn(c) for c in LABEL_COLORS],
            spacing=8,
            wrap=True,
        )

        def _select_color(c: str) -> None:
            nonlocal selected_color
            selected_color = c
            color_row.controls = [_make_color_btn(c2) for c2 in LABEL_COLORS]
            self.page.update()

        error_text = ft.Text("", color=PALETTE["state.danger"], size=12)

        def _save(e: Any) -> None:
            name = (name_field.value or "").strip()
            if not name:
                error_text.value = "Nama label tidak boleh kosong"
                self.page.update()
                return
            labels_list = labels_repo.list_labels(self.conn)
            for lb in labels_list:
                if lb.name == name and (not is_edit or (label and lb.id != label.id)):
                    error_text.value = "Nama label sudah ada"
                    self.page.update()
                    return
            error_text.value = ""
            if is_edit and label:
                label.name = name
                label.color = selected_color
                label.description = (desc_field.value or "").strip()
                labels_repo.update_label(self.conn, label)
            else:
                labels_repo.create_label(
                    self.conn,
                    Label(
                        id=None,
                        name=name,
                        color=selected_color,
                        description=(desc_field.value or "").strip(),
                    ),
                )
            self.page.pop_dialog()
            self.refresh()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Label" if is_edit else "Tambah Label"),
            content=ft.Column(
                [name_field, error_text, desc_field, color_row],
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

    def _delete(self, label: Label) -> None:
        def _confirm(e: Any) -> None:
            labels_repo.delete_label(self.conn, label.id)  # type: ignore[arg-type]
            self.page.pop_dialog()
            self.refresh()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Hapus label?"),
            content=ft.Text(f'"{label.name}" akan dihapus.'),
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
        labels = labels_repo.list_labels(self.conn)
        counts = labels_repo.get_label_item_counts(self.conn)
        all_prompts = prompts_repo.list_prompts(self.conn)
        all_commands = commands_repo.list_commands(self.conn)
        all_api_refs = api_refs_repo.list_api_refs(self.conn)
        self.list_area.controls.clear()

        if not labels:
            self.list_area.controls.append(
                self.empty_state("Belum ada label. Tambahkan yang pertama!")
            )
        else:
            for lb in labels:
                item_counts = counts.get(lb.id, {}) if lb.id else {}
                self.list_area.controls.append(
                    self._label_section(
                        lb, item_counts,
                        all_prompts, all_commands, all_api_refs,
                    )
                )
        self.page.update()

    def _label_section(
        self,
        label: Label,
        item_counts: dict[str, int],
        all_prompts: list[Prompt],
        all_commands: list[Command],
        all_api_refs: list[ApiRef],
    ) -> ft.Container:
        total = sum(item_counts.values())

        label_prompt_ids = set(
            labels_repo.get_items_by_label(self.conn, label.id, "prompts")  # type: ignore[arg-type]
        )
        label_cmd_ids = set(
            labels_repo.get_items_by_label(self.conn, label.id, "commands")  # type: ignore[arg-type]
        )
        label_api_ids = set(
            labels_repo.get_items_by_label(self.conn, label.id, "api_refs")  # type: ignore[arg-type]
        )

        filtered_prompts = [p for p in all_prompts if p.id in label_prompt_ids]
        filtered_commands = [c for c in all_commands if c.id in label_cmd_ids]
        filtered_api_refs = [r for r in all_api_refs if r.id in label_api_ids]

        content_controls: list[ft.Control] = []

        if filtered_prompts:
            content_controls.append(
                ft.Text("Prompts", size=13, weight=ft.FontWeight.W_600,
                        color=PALETTE["accent.mint"])
            )
            for p in filtered_prompts:
                content_controls.append(self._prompt_item(p))

        if filtered_commands:
            content_controls.append(
                ft.Text("Commands", size=13, weight=ft.FontWeight.W_600,
                        color=PALETTE["accent.mint"])
            )
            for c in filtered_commands:
                content_controls.append(self._command_item(c))

        if filtered_api_refs:
            content_controls.append(
                ft.Text("API References", size=13, weight=ft.FontWeight.W_600,
                        color=PALETTE["accent.mint"])
            )
            for r in filtered_api_refs:
                content_controls.append(self._api_item(r))

        if not content_controls:
            content_controls.append(
                ft.Text("(Belum ada item)", size=12, color=PALETTE["text.secondary"])
            )

        header = ft.Row(
            [
                ft.Container(
                    width=12,
                    height=12,
                    bgcolor=label.color,
                    border_radius=6,
                ),
                ft.Text(
                    label.name,
                    size=16,
                    weight=ft.FontWeight.W_600,
                    color=PALETTE["text.primary"],
                ),
                ft.Text(
                    f"{total} item{'s' if total != 1 else ''}",
                    size=12,
                    color=PALETTE["text.secondary"],
                ),
                ft.Container(expand=True),
                action_button(
                    ft.Icons.EDIT_OUTLINED,
                    "Edit",
                    lambda e, lb=label: self._open_edit(lb),
                ),
                action_button(
                    ft.Icons.DELETE_OUTLINE,
                    "Hapus",
                    lambda e, lb=label: self._delete(lb),
                    danger=True,
                ),
            ],
            spacing=6,
            alignment=ft.MainAxisAlignment.START,
        )

        return ft.Container(
            content=ft.Column(
                [
                    header,
                    ft.Divider(height=1, color=PALETTE["border.subtle"]),
                    ft.Column(content_controls, spacing=4),
                ],
                spacing=4,
            ),
            bgcolor=PALETTE["bg.surface"],
            border=ft.Border.all(1, PALETTE["border.subtle"]),
            border_radius=8,
            padding=12,
        )

    def _prompt_item(self, p: Prompt) -> ft.Container:
        labels = labels_repo.get_labels_for_item(self.conn, "prompts", p.id)  # type: ignore[arg-type]
        label_chips = ft.Row(
            [label_chip(lb) for lb in labels], spacing=4
        ) if labels else ft.Container()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            copy_button(
                                ft.Icons.CONTENT_COPY,
                                "Copy",
                                lambda: copy_to_clipboard(
                                    self.page, p.content,
                                    f'Prompt "{p.title}" disalin.',
                                ),
                                accent=False,
                            ),
                            ft.Text(
                                p.title,
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=PALETTE["text.primary"],
                            ),
                            ft.Container(
                                content=ft.Text(
                                    p.tool,
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
                        spacing=4,
                    ),
                    label_chips,
                    ft.Text(
                        (p.content or "")[:100]
                        + ("…" if len(p.content or "") > 100 else ""),
                        size=12,
                        color=PALETTE["text.secondary"],
                        max_lines=2,
                    ),
                ],
                spacing=2,
            ),
            bgcolor=PALETTE["bg.surface-hover"],
            border_radius=6,
            padding=8,
        )

    def _command_item(self, cmd: Command) -> ft.Container:
        labels = labels_repo.get_labels_for_item(self.conn, "commands", cmd.id)  # type: ignore[arg-type]
        label_chips = ft.Row(
            [label_chip(lb) for lb in labels], spacing=4
        ) if labels else ft.Container()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.CONTENT_COPY,
                                icon_color=PALETTE["text.secondary"],
                                tooltip="Copy",
                                on_click=lambda e, c=cmd: copy_to_clipboard(
                                    self.page, c.command_text,
                                    f'Command "{c.title}" disalin.',
                                ),
                            ),
                            ft.Text(
                                cmd.title,
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=PALETTE["text.primary"],
                            ),
                        ],
                        spacing=4,
                    ),
                    label_chips,
                    ft.Text(
                        cmd.command_text[:80]
                        + ("…" if len(cmd.command_text) > 80 else ""),
                        size=12,
                        color=PALETTE["accent.mint"],
                        style=ft.TextStyle(font_family="monospace"),
                    ),
                ],
                spacing=2,
            ),
            bgcolor=PALETTE["bg.surface-hover"],
            border_radius=6,
            padding=8,
        )

    def _api_item(self, ref: ApiRef) -> ft.Container:
        labels = labels_repo.get_labels_for_item(self.conn, "api_refs", ref.id)  # type: ignore[arg-type]
        label_chips = ft.Row(
            [label_chip(lb) for lb in labels], spacing=4
        ) if labels else ft.Container()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.KEY_OUTLINED,
                                icon_color=PALETTE["state.success"],
                                tooltip="Copy key",
                                on_click=lambda e: self._copy_api(ref),
                            ),
                            ft.Text(
                                ref.service_name,
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=PALETTE["text.primary"],
                            ),
                        ],
                        spacing=4,
                    ),
                    label_chips,
                    ft.Text(
                        ref.base_url,
                        size=12,
                        color=PALETTE["accent.mint"],
                        style=ft.TextStyle(font_family="monospace"),
                    ),
                ],
                spacing=2,
            ),
            bgcolor=PALETTE["bg.surface-hover"],
            border_radius=6,
            padding=8,
        )


    def _copy_api(self, ref: ApiRef) -> None:
        secret = get_secret(ref.keychain_key_name or ref.service_name)
        target = secret or ref.base_url or ref.service_name
        copy_to_clipboard(
            self.page, target,
            f'API key "{ref.service_name}" disalin!',
        )
