"""View modul Docs — file manager + split-pane markdown editor."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import flet as ft

from src.app.components.cards import (
    build_label_checkboxes,
    get_selected_label_ids,
)
from src.app.components.markdown_view import render_markdown
from src.app.theme import PALETTE
from src.app.views.base import BaseView
from src.core.models import DocFile, DocFolder
from src.core.storage import doc_files_repo, doc_folders_repo, labels_repo

MD_EXTENSIONS = {".md", ".markdown", ".mdown", ".mkd"}

FOLDER_COLORS: list[str] = [
    "#6C8CFF",
    "#2DD4BF",
    "#F5A623",
    "#F5484B",
    "#3DDC84",
    "#E879F9",
    "#FB923C",
    "#60A5FA",
]


class DocsView(BaseView):
    """View untuk file manager + markdown editor."""

    def __init__(self, page: ft.Page, conn: sqlite3.Connection) -> None:
        super().__init__(
            page, "Docs", ft.Icons.DESCRIPTION_OUTLINED, self._open_add_file
        )
        self.conn = conn
        self._selected_folder_id: int | None = None
        self._selected_file_id: int | None = None
        self._editor_textfield: ft.TextField | None = None
        self._editor_preview: ft.Container | None = None
        self._file_list_area: ft.Column = ft.Column(spacing=4, expand=True)
        self._folder_tree_area: ft.Column = ft.Column(spacing=2, expand=True)
        self._editor_container: ft.Container = ft.Container(expand=True)
        self._editor_divider: ft.VerticalDivider = ft.VerticalDivider(
            width=1, color=PALETTE["border.subtle"]
        )
        self._breadcrumb: ft.Row = ft.Row(spacing=4)
        self._toolbar: ft.Row = ft.Row(spacing=2)
        self._expanded_folder_ids: set[int] = set()
        self._tree_needs_refresh = False

    # ------------------------------------------------------------------
    # Custom build — 2-panel layout, editor hidden until file clicked
    # ------------------------------------------------------------------

    def build(self) -> ft.Container:
        folder_panel = self._build_folder_panel()
        file_panel = self._build_file_panel()
        editor_panel = self._build_editor_panel()

        self._editor_container.visible = False
        self._editor_divider.visible = False

        self._refresh_folder_tree()
        self._refresh_file_list()
        self._refresh_breadcrumb()
        self.page.update()

        return ft.Container(
            content=ft.Column(
                [
                    self._build_top_bar(),
                    ft.Divider(height=1, color=PALETTE["border.subtle"]),
                    ft.Row(
                        [
                            folder_panel,
                            ft.VerticalDivider(
                                width=1, color=PALETTE["border.subtle"]
                            ),
                            file_panel,
                            self._editor_divider,
                            editor_panel,
                        ],
                        expand=True,
                        spacing=0,
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            padding=0,
            expand=True,
        )

    def _build_top_bar(self) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        self.icon,
                        color=PALETTE["accent.primary"],
                        size=22,
                    ),
                    ft.Text(
                        self.title,
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=PALETTE["text.primary"],
                    ),
                    ft.Container(expand=True),
                    self._breadcrumb,
                ],
                spacing=8,
            ),
            padding=ft.Padding.symmetric(horizontal=24, vertical=12),
        )

    # ------------------------------------------------------------------
    # Folder panel
    # ------------------------------------------------------------------

    def _build_folder_panel(self) -> ft.Container:
        add_folder_btn = ft.IconButton(
            icon=ft.Icons.CREATE_NEW_FOLDER_OUTLINED,
            icon_color=PALETTE["accent.primary"],
            icon_size=18,
            tooltip="New Folder",
            on_click=lambda e: self._open_add_folder(),
        )
        upload_btn = ft.IconButton(
            icon=ft.Icons.UPLOAD_FILE_OUTLINED,
            icon_color=PALETTE["accent.primary"],
            icon_size=18,
            tooltip="Upload Folder",
            on_click=lambda e: self._upload_folder(),
        )

        root_item = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.FOLDER_OFF_OUTLINED,
                        size=16,
                        color=PALETTE["text.secondary"],
                    ),
                    ft.Text(
                        "All Files",
                        size=13,
                        color=PALETTE["text.secondary"],
                    ),
                ],
                spacing=6,
            ),
            padding=ft.Padding.symmetric(horizontal=8, vertical=6),
            border_radius=6,
            on_click=lambda e: self._select_folder(None),
            ink=True,
        )

        self._folder_tree_area.controls.clear()
        self._folder_tree_area.controls.append(root_item)
        self._build_folder_tree(None, 0)

        return ft.Container(
            width=240,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "Folders",
                                size=12,
                                weight=ft.FontWeight.W_600,
                                color=PALETTE["text.secondary"],
                            ),
                            ft.Container(expand=True),
                            upload_btn,
                            add_folder_btn,
                        ],
                        spacing=4,
                    ),
                    ft.Divider(height=1, color=PALETTE["border.subtle"]),
                    self._folder_tree_area,
                ],
                spacing=4,
                expand=True,
            ),
            bgcolor=PALETTE["bg.surface"],
            border=ft.Border.all(1, PALETTE["border.subtle"]),
            border_radius=8,
            padding=8,
            margin=ft.Margin.all(12),
        )

    def _build_folder_tree(self, parent_id: int | None, depth: int) -> None:
        if parent_id is None:
            folders = doc_folders_repo.list_root_folders(self.conn)
        else:
            folders = doc_folders_repo.get_children(self.conn, parent_id)

        for folder in folders:
            indent = 8 + depth * 16
            is_selected = self._selected_folder_id == folder.id
            file_count = doc_folders_repo.count_files_in_folder(
                self.conn, folder.id  # type: ignore[arg-type]
            )
            children = doc_folders_repo.get_children(
                self.conn, folder.id  # type: ignore[arg-type]
            )
            has_children = len(children) > 0

            folder_menu = ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.EDIT_OUTLINED, size=16),
                                ft.Text("Rename", size=13),
                            ],
                            spacing=8,
                        ),
                        on_click=lambda e, fb=folder: self._open_edit_folder(
                            fb
                        ),
                    ),
                    ft.PopupMenuItem(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.DELETE_OUTLINE, size=16),
                                ft.Text("Delete", size=13),
                            ],
                            spacing=8,
                        ),
                        on_click=lambda e, fid=folder.id: self._delete_folder(
                            fid  # type: ignore[arg-type]
                        ),
                    ),
                ],
                icon_color=PALETTE["text.secondary"],
                icon_size=16,
                tooltip="Actions",
            )

            folder_row = ft.Row(
                [
                    ft.Icon(
                        ft.Icons.FOLDER
                        if has_children
                        else ft.Icons.FOLDER_OUTLINED,
                        size=16,
                        color=folder.color,
                    ),
                    ft.Container(
                        width=8,
                        height=8,
                        bgcolor=folder.color,
                        border_radius=4,
                    ),
                    ft.Text(
                        folder.name,
                        size=13,
                        color=PALETTE["text.primary"]
                        if is_selected
                        else PALETTE["text.secondary"],
                        weight=ft.FontWeight.W_600
                        if is_selected
                        else ft.FontWeight.NORMAL,
                        expand=True,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        str(file_count),
                        size=10,
                        color=PALETTE["text.secondary"],
                    ),
                    folder_menu,
                ],
                spacing=2,
            )

            folder_item = ft.Container(
                content=folder_row,
                padding=ft.Padding.symmetric(
                    horizontal=float(indent), vertical=6
                ),
                border_radius=6,
                bgcolor=PALETTE["accent.primary"]
                if is_selected
                else PALETTE["bg.base"],
                on_click=lambda e, fid=folder.id: self._select_folder(fid),
                ink=True,
            )
            self._folder_tree_area.controls.append(folder_item)

            if has_children:
                self._build_folder_tree(folder.id, depth + 1)

    # ------------------------------------------------------------------
    # File panel
    # ------------------------------------------------------------------

    def _build_file_panel(self) -> ft.Container:
        add_file_btn = ft.IconButton(
            icon=ft.Icons.NOTE_ADD_OUTLINED,
            icon_color=PALETTE["accent.primary"],
            icon_size=18,
            tooltip="New File",
            on_click=lambda e: self._open_add_file(),
        )

        self._file_list_area.controls.clear()
        self._refresh_file_list()

        return ft.Container(
            width=250,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "Files",
                                size=12,
                                weight=ft.FontWeight.W_600,
                                color=PALETTE["text.secondary"],
                            ),
                            ft.Container(expand=True),
                            add_file_btn,
                        ],
                        spacing=4,
                    ),
                    ft.Divider(height=1, color=PALETTE["border.subtle"]),
                    self._file_list_area,
                ],
                spacing=4,
                expand=True,
            ),
            bgcolor=PALETTE["bg.surface"],
            border=ft.Border.all(1, PALETTE["border.subtle"]),
            border_radius=8,
            padding=8,
            margin=ft.Margin.only(top=12, bottom=12, right=12),
        )

    # ------------------------------------------------------------------
    # Editor panel (hidden until file clicked)
    # ------------------------------------------------------------------

    def _build_editor_panel(self) -> ft.Container:
        self._editor_textfield = ft.TextField(
            multiline=True,
            min_lines=20,
            max_lines=40,
            text_style=ft.TextStyle(
                size=14,
                color=PALETTE["text.primary"],
            ),
            bgcolor=PALETTE["bg.base"],
            border_color=PALETTE["border.subtle"],
            border_radius=8,
            content_padding=12,
            hint_text="Start typing markdown...",
            on_change=self._on_editor_change,
        )

        self._editor_preview = ft.Container(
            content=ft.Column(
                [ft.Text("", size=14, color=PALETTE["text.secondary"])],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            expand=True,
        )

        self._toolbar = ft.Row(
            [
                self._md_button("**B**", "Bold", "**", "**"),
                self._md_button("*I*", "Italic", "*", "*"),
                self._md_button("H1", "Heading 1", "# ", ""),
                self._md_button("H2", "Heading 2", "## ", ""),
                self._md_button("H3", "Heading 3", "### ", ""),
                self._md_button("</>", "Code Block", "```\n", "\n```"),
                self._md_button("`", "Inline Code", "`", "`"),
                self._md_button("- ", "List", "- ", ""),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.SAVE_OUTLINED,
                    icon_color=PALETTE["accent.primary"],
                    icon_size=18,
                    tooltip="Save",
                    on_click=lambda e: self._save_current_file(),
                ),
            ],
            spacing=4,
        )

        split_pane = ft.Row(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Editor",
                                size=11,
                                weight=ft.FontWeight.W_600,
                                color=PALETTE["text.secondary"],
                            ),
                            self._editor_textfield,
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    expand=True,
                    padding=ft.Padding.only(right=4),
                ),
                ft.VerticalDivider(
                    width=1, color=PALETTE["border.subtle"]
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Preview",
                                size=11,
                                weight=ft.FontWeight.W_600,
                                color=PALETTE["text.secondary"],
                            ),
                            self._editor_preview,
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    expand=True,
                    padding=ft.Padding.only(left=4),
                ),
            ],
            expand=True,
            spacing=0,
        )

        self._editor_container = ft.Container(
            content=ft.Column(
                [
                    self._toolbar,
                    ft.Divider(
                        height=1, color=PALETTE["border.subtle"]
                    ),
                    split_pane,
                ],
                spacing=4,
                expand=True,
            ),
            bgcolor=PALETTE["bg.surface"],
            border=ft.Border.all(1, PALETTE["border.subtle"]),
            border_radius=8,
            padding=12,
            margin=ft.Margin.only(top=12, bottom=12, right=12),
            expand=True,
        )

        return self._editor_container

    def _md_button(
        self, label: str, tooltip: str, prefix: str, suffix: str
    ) -> ft.Container:
        return ft.Container(
            content=ft.Text(
                label,
                size=12,
                color=PALETTE["text.secondary"],
            ),
            bgcolor=PALETTE["bg.base"],
            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            border_radius=4,
            border=ft.Border.all(1, PALETTE["border.subtle"]),
            on_click=lambda e, p=prefix, s=suffix: self._insert_markdown(
                p, s
            ),
            tooltip=tooltip,
        )

    # ------------------------------------------------------------------
    # State management
    # ------------------------------------------------------------------

    def _select_folder(self, folder_id: int | None) -> None:
        self._selected_folder_id = folder_id
        self._selected_file_id = None
        self._hide_editor()
        self._refresh_all()

    def _select_file(self, file_id: int) -> None:
        self._selected_file_id = file_id
        self._show_editor()
        self._refresh_editor()
        self._refresh_breadcrumb()
        self._refresh_file_list()
        self.page.update()

    def _show_editor(self) -> None:
        self._editor_container.visible = True
        self._editor_divider.visible = True

    def _hide_editor(self) -> None:
        self._editor_container.visible = False
        self._editor_divider.visible = False

    def _refresh_all(self) -> None:
        self._refresh_folder_tree()
        self._refresh_file_list()
        self._refresh_breadcrumb()
        self.page.update()

    def _refresh_folder_tree(self) -> None:
        self._folder_tree_area.controls.clear()
        root_item = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.FOLDER_OFF_OUTLINED,
                        size=16,
                        color=PALETTE["text.secondary"],
                    ),
                    ft.Text(
                        "All Files",
                        size=13,
                        color=PALETTE["text.secondary"],
                    ),
                ],
                spacing=6,
            ),
            padding=ft.Padding(left=8, vertical=6),
            border_radius=6,
            on_click=lambda e: self._select_folder(None),
            ink=True,
        )
        self._folder_tree_area.controls.append(root_item)
        root_folders = doc_folders_repo.list_root_folders(self.conn)
        for folder in root_folders:
            self._folder_tree_area.controls.append(
                self._build_folder_tree_node(folder, 0)
            )

    def _build_folder_tree_node(self, folder: DocFolder, depth: int) -> ft.Column:
        children = doc_folders_repo.get_children(self.conn, folder.id)
        is_expanded = folder.id in self._expanded_folder_ids
        indent = float(8 + depth * 16)

        folder_row = ft.Row(
            [
                ft.Icon(
                    ft.Icons.CHEVRON_DOWN if is_expanded else ft.Icons.CHEVRON_RIGHT,
                    size=14,
                    color=PALETTE["text.secondary"],
                ),
                ft.Icon(
                    ft.Icons.FOLDER if children else ft.Icons.FOLDER_OUTLINED,
                    size=14,
                    color=folder.color,
                ),
                ft.Text(
                    folder.name,
                    size=13,
                    color=PALETTE["text.primary"]
                    if self._selected_folder_id == folder.id
                    else PALETTE["text.secondary"],
                    weight=ft.FontWeight.W_600
                    if self._selected_folder_id == folder.id
                    else ft.FontWeight.NORMAL,
                    expand=True,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Text(
                    str(doc_files_repo.count_files_in_folder(
                        self.conn, folder.id  # type: ignore[arg-type]
                    )),
                    size=10,
                    color=PALETTE["text.secondary"],
                ),
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.EDIT_OUTLINED, size=16),
                                    ft.Text("Rename", size=13),
                                ],
                                spacing=8,
                            ),
                            on_click=lambda e, fb=folder: self._open_edit_folder(
                                fb
                            ),
                        ),
                        ft.PopupMenuItem(
                            content=ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.DELETE_OUTLINE, size=16
                                    ),
                                    ft.Text("Delete", size=13),
                                ],
                                spacing=8,
                            ),
                            on_click=lambda e, fid=folder.id: self._delete_folder(
                                fid  # type: ignore[arg-type]
                            ),
                        ),
                    ],
                    icon_color=PALETTE["text.secondary"],
                    icon_size=14,
                    tooltip="Actions",
                ),
            ],
            spacing=2,
        )

        folder_item = ft.Container(
            content=folder_row,
            padding=ft.Padding(left=indent, vertical=4),
            border_radius=4,
            bgcolor=PALETTE["accent.primary"]
            if self._selected_folder_id == folder.id
            else PALETTE["bg.base"],
            on_click=lambda e, fid=folder.id: self._select_folder(fid),
            ink=True,
        )

        child_columns: list[ft.Control] = []
        if is_expanded and children:
            for child in children:
                child_columns.append(
                    self._build_folder_tree_node(child, depth + 1)
                )

        if child_columns:
            return ft.Column(
                controls=[folder_item] + child_columns,
                spacing=0,
            )
        return ft.Column(
            controls=[folder_item],
            spacing=0,
        )

    def _toggle_expand(self, folder_id: int) -> None:
        if folder_id in self._expanded_folder_ids:
            self._expanded_folder_ids.discard(folder_id)
        else:
            self._expanded_folder_ids.add(folder_id)
        self._refresh_folder_tree()
        self.page.update()

    def _refresh_file_list(self) -> None:
        self._file_list_area.controls.clear()

        if self._selected_folder_id is None:
            files = doc_files_repo.list_files_by_folder(self.conn, None)
        else:
            files = doc_files_repo.list_files_by_folder(
                self.conn, self._selected_folder_id
            )

        if not files:
            self._file_list_area.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.NOTE_OUTLINED,
                                size=32,
                                color=PALETTE["text.secondary"],
                            ),
                            ft.Text(
                                "No files yet",
                                size=13,
                                color=PALETTE["text.secondary"],
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    padding=24,
                    alignment=ft.Alignment(0, 0),
                )
            )
        else:
            for f in files:
                is_selected = self._selected_file_id == f.id
                preview = (f.content or "")[:60]
                if len(f.content or "") > 60:
                    preview += "..."

                file_menu = ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.EDIT_OUTLINED, size=16),
                                    ft.Text("Rename", size=13),
                                ],
                                spacing=8,
                            ),
                            on_click=lambda e, df=f: self._open_file_dialog(
                                df
                            ),
                        ),
                        ft.PopupMenuItem(
                            content=ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.DELETE_OUTLINE, size=16
                                    ),
                                    ft.Text("Delete", size=13),
                                ],
                                spacing=8,
                            ),
                            on_click=lambda e, fid=f.id: self._delete_file(
                                fid
                            ),
                        ),
                    ],
                    icon_color=PALETTE["text.secondary"],
                    icon_size=14,
                    tooltip="Actions",
                )

                item = ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.DESCRIPTION_OUTLINED,
                                        size=14,
                                        color=PALETTE["accent.mint"],
                                    ),
                                    ft.Text(
                                        f.title,
                                        size=13,
                                        weight=ft.FontWeight.W_600
                                        if is_selected
                                        else ft.FontWeight.NORMAL,
                                        color=PALETTE["text.primary"]
                                        if is_selected
                                        else PALETTE["text.secondary"],
                                        expand=True,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    file_menu,
                                ],
                                spacing=2,
                            ),
                            ft.Text(
                                preview,
                                size=11,
                                color=PALETTE["text.secondary"],
                                max_lines=1,
                            ),
                        ],
                        spacing=2,
                    ),
                    bgcolor=PALETTE["accent.primary"]
                    if is_selected
                    else PALETTE["bg.base"],
                    border_radius=6,
                    padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                    on_click=lambda e, fid=f.id: self._select_file(fid),
                    ink=True,
                )
                self._file_list_area.controls.append(item)

    def _refresh_editor(self) -> None:
        if self._editor_textfield is None:
            return

        if self._selected_file_id is None:
            self._editor_textfield.value = ""
            return

        doc_file = doc_files_repo.get_file(
            self.conn, self._selected_file_id
        )
        if doc_file is None:
            self._editor_textfield.value = ""
            return

        self._editor_textfield.value = doc_file.content
        self._update_preview(doc_file.content)

    def _refresh_breadcrumb(self) -> None:
        self._breadcrumb.controls.clear()

        self._breadcrumb.controls.append(
            ft.Text(
                "Docs",
                size=12,
                color=PALETTE["text.secondary"],
                weight=ft.FontWeight.W_600,
            )
        )

        if self._selected_folder_id is not None:
            path = self._get_folder_path(self._selected_folder_id)
            for folder in path:
                self._breadcrumb.controls.append(
                    ft.Text(
                        "/", size=12, color=PALETTE["text.secondary"]
                    )
                )
                self._breadcrumb.controls.append(
                    ft.Text(
                        folder.name,
                        size=12,
                        color=PALETTE["text.primary"],
                    )
                )

        if self._selected_file_id is not None:
            doc_file = doc_files_repo.get_file(
                self.conn, self._selected_file_id
            )
            if doc_file:
                self._breadcrumb.controls.append(
                    ft.Text(
                        "/", size=12, color=PALETTE["text.secondary"]
                    )
                )
                self._breadcrumb.controls.append(
                    ft.Text(
                        doc_file.title,
                        size=12,
                        color=PALETTE["accent.primary"],
                    )
                )

    def _get_folder_path(self, folder_id: int) -> list[DocFolder]:
        path: list[DocFolder] = []
        current_id: int | None = folder_id
        while current_id is not None:
            folder = doc_folders_repo.get_folder(self.conn, current_id)
            if folder is None:
                break
            path.insert(0, folder)
            current_id = folder.parent_id
        return path

    # ------------------------------------------------------------------
    # Editor helpers
    # ------------------------------------------------------------------

    def _on_editor_change(self, e: ft.ControlEvent | None = None) -> None:
        if self._editor_textfield is not None:
            content = self._editor_textfield.value or ""
        else:
            content = ""
        self._update_preview(content)

    def _update_preview(self, content: str) -> None:
        if self._editor_preview is None:
            return
        self._editor_preview.content = ft.Column(
            [render_markdown(content)],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _insert_markdown(self, prefix: str, suffix: str) -> None:
        if self._editor_textfield is None:
            return
        tf = self._editor_textfield
        current = tf.value or ""
        new_text = current + prefix + suffix
        tf.value = new_text
        self._update_preview(new_text)
        self.page.update()

    def _save_current_file(self) -> None:
        if self._selected_file_id is None:
            return
        doc_file = doc_files_repo.get_file(
            self.conn, self._selected_file_id
        )
        if doc_file is None or self._editor_textfield is None:
            return
        doc_file.content = self._editor_textfield.value or ""
        doc_files_repo.update_file(self.conn, doc_file)
        snack = ft.SnackBar(
            ft.Text(f'File "{doc_file.title}" saved.'),
            bgcolor=PALETTE["state.success"],
        )
        self.page.overlay.append(snack)
        snack.open = True
        self.page.update()

    # ------------------------------------------------------------------
    # Upload folder from filesystem
    # ------------------------------------------------------------------

    def _upload_folder(self) -> None:
        async def _do_upload() -> None:
            picker = ft.FilePicker()
            path = await picker.get_directory_path(
                dialog_title="Select folder to import"
            )
            if path:
                self._import_folder_from_path(path)
                self._refresh_all()
        self.page.run_task(_do_upload)

    def _import_folder_from_path(self, path: str) -> None:
        root = Path(path)
        if not root.is_dir():
            return
        parent_id = self._selected_folder_id
        self._import_recursive(root, parent_id, 0)

    def _import_recursive(
        self, path: Path, parent_id: int | None, depth: int
    ) -> None:
        if depth >= MAX_FOLDER_DEPTH:
            return
        for entry in sorted(path.iterdir()):
            if entry.name.startswith("."):
                continue
            if entry.is_dir():
                folder = doc_folders_repo.create_folder(
                    self.conn,
                    DocFolder(
                        id=None,
                        name=entry.name,
                        parent_id=parent_id,
                    ),
                )
                self._import_recursive(entry, folder.id, depth + 1)
            elif (
                entry.is_file()
                and entry.suffix.lower() in MD_EXTENSIONS
            ):
                try:
                    content = entry.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    content = ""
                doc_files_repo.create_file(
                    self.conn,
                    DocFile(
                        id=None,
                        title=entry.name,
                        content=content,
                        folder_id=parent_id,
                    ),
                )

    # ------------------------------------------------------------------
    # CRUD dialogs
    # ------------------------------------------------------------------

    def _open_add_folder(self) -> None:
        self._open_folder_dialog(None)

    def _open_edit_folder(self, folder: DocFolder) -> None:
        self._open_folder_dialog(folder)

    def _open_folder_dialog(self, folder: DocFolder | None) -> None:
        is_edit = folder is not None
        name_field = ft.TextField(
            label="Folder Name",
            value=folder.name if folder else "",
            dense=True,
        )

        selected_color = folder.color if folder else FOLDER_COLORS[0]

        def _make_color_btn(hex_color: str) -> ft.Container:
            is_sel = selected_color == hex_color
            return ft.Container(
                width=24,
                height=24,
                bgcolor=hex_color,
                border_radius=12,
                border=ft.Border.all(
                    2,
                    PALETTE["text.primary"]
                    if is_sel
                    else PALETTE["bg.base"],
                ),
                on_click=lambda e, c=hex_color: _select_color(c),
            )

        color_row = ft.Row(
            [_make_color_btn(c) for c in FOLDER_COLORS],
            spacing=6,
            wrap=True,
        )

        def _select_color(c: str) -> None:
            nonlocal selected_color
            selected_color = c
            color_row.controls = [
                _make_color_btn(c2) for c2 in FOLDER_COLORS
            ]
            self.page.update()

        all_labels = labels_repo.list_labels(self.conn)
        current_label_ids = folder.label_ids if folder else []
        label_checks, label_section = build_label_checkboxes(
            all_labels, current_label_ids
        )

        error_text = ft.Text(
            "", color=PALETTE["state.danger"], size=12
        )

        def _save(e: Any) -> None:
            name = (name_field.value or "").strip()
            if not name:
                error_text.value = "Folder name cannot be empty"
                self.page.update()
                return

            if is_edit and folder:
                folder.name = name
                folder.color = selected_color
                folder.label_ids = get_selected_label_ids(label_checks)
                doc_folders_repo.update_folder(self.conn, folder)
            else:
                depth = 0
                if self._selected_folder_id is not None:
                    depth = doc_folders_repo.get_folder_depth(
                        self.conn, self._selected_folder_id
                    ) + 1
                if depth >= MAX_FOLDER_DEPTH:
                    error_text.value = (
                        f"Maximum folder depth is"
                        f" {MAX_FOLDER_DEPTH} levels"
                    )
                    self.page.update()
                    return
                doc_folders_repo.create_folder(
                    self.conn,
                    DocFolder(
                        id=None,
                        name=name,
                        parent_id=self._selected_folder_id,
                        color=selected_color,
                        label_ids=get_selected_label_ids(
                            label_checks
                        ),
                    ),
                )
            self.page.pop_dialog()
            self._refresh_all()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Edit Folder" if is_edit else "New Folder"
            ),
            content=ft.Column(
                [name_field, error_text, color_row, label_section],
                spacing=8,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=lambda e: self.page.pop_dialog(),
                ),
                ft.FilledButton("Save", on_click=_save),
            ],
        )
        self.page.show_dialog(dialog)

    def _open_add_file(self) -> None:
        self._open_file_dialog(None)

    def _open_file_dialog(self, doc_file: DocFile | None) -> None:
        is_edit = doc_file is not None
        title_field = ft.TextField(
            label="File Name",
            value=doc_file.title if doc_file else "",
            dense=True,
        )

        def _save(e: Any) -> None:
            title = (title_field.value or "").strip()
            if not title:
                return
            if not title.endswith(".md"):
                title += ".md"

            if is_edit and doc_file:
                doc_file.title = title
                doc_files_repo.update_file(self.conn, doc_file)
            else:
                new_file = doc_files_repo.create_file(
                    self.conn,
                    DocFile(
                        id=None,
                        title=title,
                        content="",
                        folder_id=self._selected_folder_id,
                    ),
                )
                self._selected_file_id = new_file.id

            self.page.pop_dialog()
            self._refresh_all()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Edit File" if is_edit else "New File"
            ),
            content=ft.Column(
                [title_field],
                spacing=8,
                tight=True,
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=lambda e: self.page.pop_dialog(),
                ),
                ft.FilledButton("Save", on_click=_save),
            ],
        )
        self.page.show_dialog(dialog)

    def _delete_file(self, file_id: int) -> None:
        doc_file = doc_files_repo.get_file(self.conn, file_id)
        if doc_file is None:
            return

        def _confirm(e: Any) -> None:
            doc_files_repo.delete_file(self.conn, file_id)
            if self._selected_file_id == file_id:
                self._selected_file_id = None
                self._hide_editor()
            self.page.pop_dialog()
            self._refresh_all()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete file?"),
            content=ft.Text(
                f'"{doc_file.title}" will be deleted.'
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=lambda e: self.page.pop_dialog(),
                ),
                ft.FilledButton(
                    "Delete",
                    bgcolor=PALETTE["state.danger"],
                    on_click=_confirm,
                ),
            ],
        )
        self.page.show_dialog(dialog)

    def _delete_folder(self, folder_id: int) -> None:
        folder = doc_folders_repo.get_folder(self.conn, folder_id)
        if folder is None:
            return

        file_count = doc_folders_repo.count_files_in_folder(
            self.conn, folder_id
        )
        child_folders = doc_folders_repo.get_children(
            self.conn, folder_id
        )

        def _confirm(e: Any) -> None:
            doc_folders_repo.delete_folder(self.conn, folder_id)
            if self._selected_folder_id == folder_id:
                self._selected_folder_id = None
                self._selected_file_id = None
                self._hide_editor()
            self.page.pop_dialog()
            self._refresh_all()

        warning = (
            f'{file_count} file'
            f'{"s" if file_count != 1 else ""}'
        )
        if child_folders:
            child_count = len(child_folders)
            suffix = "s" if child_count != 1 else ""
            warning += (
                f" + {child_count} sub-folder{suffix}"
            )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete folder?"),
            content=ft.Text(
                f'"{folder.name}" and {warning} will be deleted.'
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=lambda e: self.page.pop_dialog(),
                ),
                ft.FilledButton(
                    "Delete",
                    bgcolor=PALETTE["state.danger"],
                    on_click=_confirm,
                ),
            ],
        )
        self.page.show_dialog(dialog)

    # ------------------------------------------------------------------
    # Refresh (BaseView interface)
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        self._refresh_all()
