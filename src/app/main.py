"""Entry point aplikasi DevCodex."""

from __future__ import annotations

import sqlite3
from typing import Any

import flet as ft

from src.app.components.sidebar import Sidebar
from src.app.theme import PALETTE
from src.app.views.api_refs_view import ApiRefsView
from src.app.views.base import BaseView
from src.app.views.commands_view import CommandsView
from src.app.views.labels_view import LabelsView
from src.app.views.prompts_view import PromptsView
from src.core.io import export_to_json, import_from_json
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

        self.sidebar.set_export_import_handlers(
            self._export_data, self._import_data
        )

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
        self._update_badges()
        self.page.update()

    def _update_badges(self) -> None:
        """Update badge counters untuk semua modul."""
        from src.core.storage import (
            api_refs_repo,
            commands_repo,
            labels_repo,
            prompts_repo,
        )

        self.sidebar.update_badge("labels", len(labels_repo.list_labels(self.conn)))
        self.sidebar.update_badge(
            "prompts", len(prompts_repo.list_prompts(self.conn))
        )
        self.sidebar.update_badge(
            "commands", len(commands_repo.list_commands(self.conn))
        )
        self.sidebar.update_badge(
            "api_refs", len(api_refs_repo.list_api_refs(self.conn))
        )

    def _open_result(self, module: str, title: str) -> None:
        self._navigate(module)

    def _on_keyboard(self, e: ft.KeyboardEvent) -> None:
        if e.key == "N" and e.meta:
            view = self.views.get(self.current_key)
            if view:
                view.on_add()
                self.page.update()
        elif e.key == "F" and e.meta:
            pass  # Cmd+F: search field focus (handled by sidebar click)
        elif e.key == "E" and e.meta:
            self._export_data()

    def _export_data(self) -> None:
        """Export semua data ke JSON file."""
        from pathlib import Path

        desktop = Path.home() / "Desktop"
        file_path = desktop / "devcodex_export.json"
        try:
            export_to_json(self.conn, file_path)
            snack = ft.SnackBar(
                ft.Text(f"Data diekspor ke {file_path}"),
                bgcolor="#3DDC84",
            )
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()
        except Exception as ex:
            snack = ft.SnackBar(
                ft.Text(f"Gagal export: {ex}"),
                bgcolor="#F5484B",
            )
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()

    def _import_data(self) -> None:
        """Import data dari JSON file."""
        from pathlib import Path

        desktop = Path.home() / "Desktop"
        file_path = desktop / "devcodex_export.json"
        if not file_path.exists():
            snack = ft.SnackBar(
                ft.Text(f"File {file_path} tidak ditemukan."),
                bgcolor="#F5484B",
            )
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()
            return

        def _confirm_import(e: Any) -> None:
            try:
                counts = import_from_json(self.conn, file_path, merge=True)
                self.page.pop_dialog()
                for key in self.views:
                    self.views[key].refresh()
                self._navigate(self.current_key)
                total = sum(counts.values())
                snack = ft.SnackBar(
                    ft.Text(f"Import selesai: {total} item ditambahkan."),
                    bgcolor="#3DDC84",
                )
                self.page.overlay.append(snack)
                snack.open = True
                self.page.update()
            except Exception as ex:
                self.page.pop_dialog()
                snack = ft.SnackBar(
                    ft.Text(f"Gagal import: {ex}"),
                    bgcolor="#F5484B",
                )
                self.page.overlay.append(snack)
                snack.open = True
                self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Import Data"),
            content=ft.Text(
                f"Import data dari {file_path}?\n"
                "Data yang sudah ada akan di-skip (merge mode)."
            ),
            actions=[
                ft.TextButton("Batal", on_click=lambda e: self.page.pop_dialog()),
                ft.FilledButton("Import", on_click=_confirm_import),
            ],
        )
        self.page.show_dialog(dialog)

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
            on_click=lambda e, k=r.module, t=r.title: self._open_result(k, t),
            ink=True,
        )


def main(page: ft.Page) -> None:
    DevCodexApp(page)


if __name__ == "__main__":
    ft.run(main)
