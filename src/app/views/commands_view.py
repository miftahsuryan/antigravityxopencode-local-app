"""View modul Commands."""

from __future__ import annotations

import sqlite3
from typing import Any

import flet as ft

from src.app.theme import PALETTE
from src.app.utils.clipboard import copy_to_clipboard
from src.app.views.base import BaseView
from src.core.models import Command
from src.core.storage import commands_repo, labels_repo


class CommandsView(BaseView):
    """View untuk CRUD command snippets."""

    def __init__(self, page: ft.Page, conn: sqlite3.Connection) -> None:
        super().__init__(page, "Commands", ft.Icons.TERMINAL_OUTLINED, self._open_add)
        self.conn = conn
        self.refresh()

    def _open_add(self) -> None:
        self._open_dialog(None)

    def _open_edit(self, cmd: Command) -> None:
        self._open_dialog(cmd)

    def _duplicate(self, cmd: Command) -> None:
        commands_repo.create_command(
            self.conn,
            Command(
                id=None,
                title=f"{cmd.title} (copy)",
                command_text=cmd.command_text,
                description=cmd.description,
                label_ids=[
                    lb.id for lb in labels_repo.get_labels_for_item(
                        self.conn, "commands", cmd.id  # type: ignore[arg-type]
                    ) if lb.id is not None
                ],
            ),
        )
        self.refresh()

    def _open_dialog(self, cmd: Command | None) -> None:
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

        all_labels = labels_repo.list_labels(self.conn)
        current_label_ids = cmd.label_ids if cmd else []
        label_checks: list[ft.Checkbox] = []
        for lb in all_labels:
            label_checks.append(
                ft.Checkbox(
                    label=lb.name,
                    value=lb.id in current_label_ids,
                    data=lb.id,
                )
            )
        label_section = ft.Column(
            controls=label_checks, spacing=2, scroll=ft.ScrollMode.AUTO  # type: ignore[arg-type]
        ) if label_checks else ft.Text(
            "Belum ada label. Buat di halaman Labels.",
            size=12,
            color=PALETTE["text.secondary"],
        )

        def _save(e: Any) -> None:
            selected_ids = [
                cb.data for cb in label_checks if cb.value  # type: ignore[attr-defined]
            ]
            if is_edit and cmd:
                cmd.title = (title_field.value or "").strip()
                cmd.command_text = (command_field.value or "").strip()
                cmd.description = desc_field.value or ""
                cmd.label_ids = selected_ids
                commands_repo.update_command(self.conn, cmd)
            else:
                commands_repo.create_command(
                    self.conn,
                    Command(
                        id=None,
                        title=(title_field.value or "").strip(),
                        command_text=(command_field.value or "").strip(),
                        description=desc_field.value or "",
                        label_ids=selected_ids,
                    ),
                )
            self.page.pop_dialog()
            self.refresh()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Command" if is_edit else "Tambah Command"),
            content=ft.Column(
                [title_field, command_field, desc_field, label_section],
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

    def refresh(self) -> None:
        commands = commands_repo.list_commands(self.conn)
        commands = self.sort_items(commands, "title")
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
        labels = labels_repo.get_labels_for_item(self.conn, "commands", cmd.id)  # type: ignore[arg-type]
        label_chips = ft.Row(
            [_label_chip(lb) for lb in labels], spacing=4
        ) if labels else ft.Container()

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
                                ft.Icons.COPY_ALL_OUTLINED,
                                "Duplicate",
                                lambda e, c=cmd: self._duplicate(c),
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
                    label_chips,
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

    def _copy(self, cmd: Command) -> None:
        copy_to_clipboard(
            self.page, cmd.command_text, f'Command "{cmd.title}" disalin.'
        )


def _label_chip(label: Any) -> ft.Container:
    return ft.Container(
        content=ft.Text(label.name, size=10, color=PALETTE["bg.base"]),
        bgcolor=label.color,
        padding=ft.Padding.symmetric(horizontal=6, vertical=1),
        border_radius=4,
    )


def _action_button(
    icon: Any, tooltip: str, on_click: Any, danger: bool = False
) -> ft.IconButton:
    return ft.IconButton(
        icon=icon,
        icon_color=PALETTE["state.danger"] if danger else PALETTE["text.secondary"],
        tooltip=tooltip,
        on_click=on_click,
    )
