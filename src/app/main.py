"""Entry point aplikasi DevCodex."""

from __future__ import annotations

import sqlite3

import flet as ft

from src.app.components.sidebar import Sidebar
from src.app.theme import PALETTE
from src.app.views.api_refs_view import ApiRefsView
from src.app.views.base import BaseView
from src.app.views.commands_view import CommandsView
from src.app.views.labels_view import LabelsView
from src.app.views.prompts_view import PromptsView
from src.core.search import SearchResult, search_all
from src.core.storage.db import init_db


class DevCodexApp:
    """Orkestrator utama aplikasi DevCodex."""

    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.conn: sqlite3.Connection = init_db()

        self.views: dict[str, BaseView] = {
            "labels": LabelsView(page, self.conn),
            "prompts": PromptsView(page, self.conn),
            "commands": CommandsView(page, self.conn),
            "api_refs": ApiRefsView(page, self.conn),
        }
        self.content_area = ft.Container(expand=True)

        self.sidebar = Sidebar(page, self._navigate, self._search)
        self.current_key: str = "labels"

        self.page.title = "DevCodex"
        self.page.bgcolor = PALETTE["bg.base"]
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0

        self.page.on_keyboard_event = self._on_keyboard

        self.page.add(
            ft.Row(
                [
                    self.sidebar.build(),
                    ft.VerticalDivider(width=1, color=PALETTE["border.subtle"]),
                    self.content_area,
                ],
                spacing=0,
                expand=True,
            )
        )

        self._navigate("labels")

    def _navigate(self, key: str) -> None:
        self.current_key = key
        self.sidebar.set_active(key)
        view = self.views[key]
        view.refresh()
        self.content_area.content = view.build()
        self.page.update()

    def _on_keyboard(self, e: ft.KeyboardEvent) -> None:
        if e.key == "N" and e.meta:
            view = self.views.get(self.current_key)
            if view:
                view.on_add()
                self.page.update()
        elif e.key == "F" and e.meta:
            pass  # Cmd+F: search field focus (handled by sidebar click)

    def _search(self, query: str) -> None:
        if not query or not query.strip():
            self._navigate(self.current_key)
            return

        results = search_all(self.conn, query)
        self.sidebar.set_active("")
        self.content_area.content = self._render_results(query, results)
        self.page.update()

    def _render_results(
        self, query: str, results: list[SearchResult]
    ) -> ft.Container:
        rows: list[ft.Control] = [
            ft.Text(
                f'Hasil untuk "{query}"',
                size=20,
                weight=ft.FontWeight.BOLD,
                color=PALETTE["text.primary"],
            ),
            ft.Divider(height=1, color=PALETTE["border.subtle"]),
        ]

        if not results:
            rows.append(
                ft.Container(
                    content=ft.Text(
                        "Tidak ada hasil yang cocok.",
                        color=PALETTE["text.secondary"],
                        italic=True,
                    ),
                    padding=24,
                )
            )
        else:
            for r in results:
                rows.append(self._result_item(r, query))

        return ft.Container(
            content=ft.Column(rows, spacing=8, scroll=ft.ScrollMode.AUTO),
            padding=24,
            expand=True,
        )

    def _result_item(self, r: SearchResult, query: str) -> ft.Container:
        module_label = {
            "labels": "Labels",
            "prompts": "Prompts",
            "commands": "Commands",
            "api_refs": "API",
        }.get(r.module, r.module)
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(
                            module_label,
                            size=11,
                            color=PALETTE["text.secondary"],
                        ),
                        bgcolor=PALETTE["bg.surface-hover"],
                        padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                        border_radius=6,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                r.title,
                                size=15,
                                weight=ft.FontWeight.W_600,
                                color=PALETTE["text.primary"],
                            ),
                            ft.Text(
                                r.snippet or "",
                                size=12,
                                color=PALETTE["text.secondary"],
                                max_lines=1,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ],
                spacing=8,
            ),
            bgcolor=PALETTE["bg.surface"],
            border=ft.Border.all(1, PALETTE["border.subtle"]),
            border_radius=8,
            padding=12,
            on_click=lambda e, k=r.module: self._navigate(k),
            ink=True,
        )


def main(page: ft.Page) -> None:
    DevCodexApp(page)


if __name__ == "__main__":
    ft.run(main)
