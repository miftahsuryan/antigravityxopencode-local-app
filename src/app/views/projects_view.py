"""View modul Projects.

List project/folder sebagai pengelompokkan prompt, command, dan API key.
Setiap project berisi item-item terkait.
"""

from __future__ import annotations

import sqlite3
from typing import Any

import flet as ft

from src.app.theme import PALETTE
from src.app.views.base import BaseView
from src.core.models import Project
from src.core.storage import projects_repo


class ProjectsView(BaseView):
    """View untuk mengelola project/folder."""

    def __init__(self, page: ft.Page, conn: sqlite3.Connection) -> None:
        super().__init__(page, "Projects", ft.Icons.FOLDER_OUTLINED, self._open_add)
        self.conn = conn
        self.refresh()

    def _open_add(self) -> None:
        self._open_dialog(None)

    def _open_edit(self, project: Project) -> None:
        self._open_dialog(project)

    def _open_dialog(self, project: Project | None) -> None:
        is_edit = project is not None
        name_field = ft.TextField(
            label="Nama Project",
            value=project.name if project else "",
            dense=True,
        )
        desc_field = ft.TextField(
            label="Deskripsi",
            value=project.description if project else "",
            dense=True,
        )

        def _save(e: Any) -> None:
            if is_edit and project:
                project.name = (name_field.value or "").strip()
                project.description = (desc_field.value or "").strip()
                projects_repo.update_project(self.conn, project)
            else:
                projects_repo.create_project(
                    self.conn,
                    Project(
                        id=None,
                        title=(name_field.value or "").strip(),
                        description=(desc_field.value or "").strip(),
                    ),
                )
            self.page.pop_dialog()
            self.refresh()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Project" if is_edit else "Tambah Project"),
            content=ft.Column(
                [name_field, desc_field],
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

    def _delete(self, project: Project) -> None:
        def _confirm(e: Any) -> None:
            projects_repo.delete_project(self.conn, project.id)
            self.page.pop_dialog()
            self.refresh()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Hapus project?"),
            content=ft.Text(f'"{project.name}" akan dihapus.'),
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
        projects = projects_repo.list_projects(self.conn)
        self.list_area.controls.clear()

        if not projects:
            self.list_area.controls.append(
                self.empty_state("Belum ada project. Tambahkan yang pertama!")
            )
        else:
            for p in projects:
                self.list_area.controls.append(self._item_card(p))
        self.page.update()

    def _item_card(self, project: Project) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.FOLDER, color=PALETTE["accent.primary"]),
                            ft.Text(
                                project.name,
                                size=16,
                                weight=ft.FontWeight.W_600,
                                color=PALETTE["text.primary"],
                            ),
                            ft.Container(expand=True),
                            _action_button(
                                ft.Icons.EDIT_OUTLINED,
                                "Edit",
                                lambda e, p=project: self._open_edit(p),
                            ),
                            _action_button(
                                ft.Icons.DELETE_OUTLINE,
                                "Hapus",
                                lambda e, p=project: self._delete(p),
                                danger=True,
                            ),
                        ],
                        spacing=4,
                    ),
                    ft.Text(
                        project.description or "(Tanpa deskripsi)",
                        size=12,
                        color=PALETTE["text.secondary"],
                    ),
                ],
                spacing=4,
            ),
            bgcolor=PALETTE["bg.surface"],
            border=ft.Border.all(1, PALETTE["border.subtle"]),
            border_radius=8,
            padding=12,
            on_click=lambda e, p=project: self._open_edit(p),
            ink=True,
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
