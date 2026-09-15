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
from src.app.views.docs_view import DocsView
from src.app.views.labels_view import LabelsView
from src.app.views.prompts_view import PromptsView
from src.core.io import export_label_to_json, import_label_from_json
from src.core.search import SearchResult, search_all
from src.core.storage import labels_repo
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
            "docs": DocsView(page, self.conn),
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
            doc_files_repo,
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
        self.sidebar.update_badge(
            "docs", doc_files_repo.count_all_files(self.conn)
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
        """Tampilkan dialog pilih label untuk export."""
        labels = labels_repo.list_labels(self.conn)
        if not labels:
            snack = ft.SnackBar(
                ft.Text("Belum ada label. Buat label terlebih dahulu."),
                bgcolor="#F5A623",
            )
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()
            return

        label_options = [
            ft.dropdown.Option(str(lb.id), lb.name) for lb in labels
        ]
        label_dropdown = ft.Dropdown(
            label="Pilih Label",
            options=label_options,
            dense=True,
        )

        def _do_export(e: Any) -> None:
            label_id_str = label_dropdown.value
            if not label_id_str:
                return
            label_id = int(label_id_str)
            from pathlib import Path

            desktop = Path.home() / "Desktop"
            label = labels_repo.get_label(self.conn, label_id)
            safe_name = (label.name if label else "export").replace(" ", "_")
            file_path = desktop / f"devcodex_{safe_name}.json"
            try:
                export_label_to_json(self.conn, file_path, label_id)
                self.page.pop_dialog()
                label_name = label.name if label else "Unknown"
                snack = ft.SnackBar(
                    ft.Text(f"Label '{label_name}' diekspor ke {file_path}"),
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

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Export Label"),
            content=ft.Column(
                [
                    ft.Text("Pilih label yang akan diexport:"),
                    label_dropdown,
                ],
                spacing=8,
                tight=True,
            ),
            actions=[
                ft.TextButton("Batal", on_click=lambda e: self.page.pop_dialog()),
                ft.FilledButton("Export", on_click=_do_export),
            ],
        )
        self.page.show_dialog(dialog)

    def _import_data(self) -> None:
        """Import data dari JSON file ke label baru."""
        from pathlib import Path

        desktop = Path.home() / "Desktop"

        # Cari file yang tersedia
        json_files = list(desktop.glob("devcodex_*.json"))
        if not json_files:
            snack = ft.SnackBar(
                ft.Text(f"File export tidak ditemukan di {desktop}"),
                bgcolor="#F5484B",
            )
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()
            return

        file_options = [
            ft.dropdown.Option(str(f), f.name) for f in json_files
        ]
        file_dropdown = ft.Dropdown(
            label="Pilih file",
            options=file_options,
            dense=True,
        )

        def _do_import(e: Any) -> None:
            selected = file_dropdown.value
            if not selected:
                return
            import_path = Path(selected)
            try:
                counts = import_label_from_json(self.conn, import_path)
                self.page.pop_dialog()
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
            title=ft.Text("Import Label"),
            content=ft.Column(
                [
                    ft.Text("Pilih file JSON yang akan diimport:"),
                    file_dropdown,
                ],
                spacing=8,
                tight=True,
            ),
            actions=[
                ft.TextButton("Batal", on_click=lambda e: self.page.pop_dialog()),
                ft.FilledButton("Import", on_click=_do_import),
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
            "doc_files": "Docs",
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
