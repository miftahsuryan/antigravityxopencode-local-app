"""Basis class untuk view modul."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import flet as ft

from src.app.theme import PALETTE

SORT_OPTIONS = [
    ("Terbaru", "newest"),
    ("Terlama", "oldest"),
    ("Nama A-Z", "name_asc"),
    ("Nama Z-A", "name_desc"),
]


class BaseView:
    """Base class untuk semua view modul."""

    def __init__(
        self,
        page: ft.Page,
        title: str,
        icon: Any,
        on_add: Callable[[], None],
    ) -> None:
        self.page = page
        self.title = title
        self.icon = icon
        self.on_add = on_add
        self._sort_key: str = "newest"
        self.list_area = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    def header(self) -> ft.Row:
        sort_dropdown = ft.Dropdown(
            width=140,
            dense=True,
            value=self._sort_key,
            options=[ft.dropdown.Option(val, lbl) for lbl, val in SORT_OPTIONS],
            on_change=self._on_sort_change,  # type: ignore[call-arg]
        )
        add_button = ft.IconButton(
            icon=ft.Icons.ADD,
            icon_color=PALETTE["accent.primary"],
            tooltip="Tambah " + self.title,
            on_click=lambda _: self.on_add(),
        )
        return ft.Row(
            [
                ft.Icon(self.icon, color=PALETTE["accent.primary"], size=22),
                ft.Text(
                    self.title,
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=PALETTE["text.primary"],
                ),
                ft.Container(expand=True),
                sort_dropdown,
                add_button,
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=8,
        )

    def _on_sort_change(self, e: Any) -> None:
        self._sort_key = e.control.value or "newest"
        self.refresh()

    def sort_items(self, items: list[Any], key_name: str = "title") -> list[Any]:
        if self._sort_key == "newest":
            return sorted(items, key=lambda x: x.updated_at or "", reverse=True)
        elif self._sort_key == "oldest":
            return sorted(items, key=lambda x: x.updated_at or "")
        elif self._sort_key == "name_asc":
            return sorted(items, key=lambda x: getattr(x, key_name, "").lower())
        elif self._sort_key == "name_desc":
            return sorted(
                items, key=lambda x: getattr(x, key_name, "").lower(), reverse=True
            )
        return items

    def empty_state(self, message: str) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.INBOX, size=48, color=PALETTE["border.subtle"]),
                    ft.Text(
                        message,
                        color=PALETTE["text.secondary"],
                        italic=True,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=48,
            alignment=ft.Alignment(0, 0),
        )

    def build(self) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    self.header(),
                    ft.Divider(height=1, color=PALETTE["border.subtle"]),
                    self.list_area,
                ],
                spacing=12,
                expand=True,
            ),
            padding=24,
            expand=True,
        )

    def refresh(self) -> None:
        raise NotImplementedError
