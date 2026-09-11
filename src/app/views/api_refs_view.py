"""View modul API References.

List referensi API + form modal tambah/edit + copy secret langsung dari Keychain.
Klik tombol salin (key icon) untuk menyalin API key langsung.
"""

from __future__ import annotations

import sqlite3
from typing import Any

import flet as ft

from src.app.theme import PALETTE
from src.app.utils.clipboard import copy_to_clipboard
from src.app.views.base import BaseView
from src.core.models import ApiRef
from src.core.secrets import get_secret, store_secret
from src.core.storage import api_refs_repo
from src.core.storage import projects_repo


class ApiRefsView(BaseView):
    """View untuk CRUD API reference."""

    def __init__(self, page: ft.Page, conn: sqlite3.Connection) -> None:
        """Inisialisasi view API References.

        Args:
            page: objek Page Flet.
            conn: koneksi SQLite yang sudah siap.
        """
        super().__init__(page, "API References", ft.Icons.CODE_OUTLINED, self._open_add)
        self.conn = conn
        self._current_filter_tag: str | None = None
        self.refresh()

    # ------------------------------------------------------------------
    # Form & dialog
    # ------------------------------------------------------------------

    def _open_add(self) -> None:
        """Buka dialog form tambah api ref baru."""
        self._open_dialog(None)

    def _open_edit(self, ref: ApiRef) -> None:
        """Buka dialog form edit api ref."""
        self._open_dialog(ref)

    def _open_dialog(self, ref: ApiRef | None) -> None:
        """Tampilkan modal form tambah/edit."""
        is_edit = ref is not None
        name_field = ft.TextField(
            label="Nama service",
            value=ref.service_name if ref else "",
            dense=True,
        )
        url_field = ft.TextField(
            label="Base URL",
            value=ref.base_url if ref else "",
            dense=True,
        )
        desc_field = ft.TextField(
            label="Deskripsi",
            value=ref.description if ref else "",
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        auth_field = ft.Dropdown(
            label="Tipe Auth",
            value=ref.auth_type if ref else "",
            options=[
                ft.dropdown.Option(""),
                ft.dropdown.Option("Bearer Token"),
                ft.dropdown.Option("API Key"),
                ft.dropdown.Option("Basic Auth"),
                ft.dropdown.Option("OAuth2"),
                ft.dropdown.Option("None"),
            ],
            dense=True,
        )
        keychain_field = ft.TextField(
            label="Nama key di Keychain (untuk secret)",
            value=ref.keychain_key_name if ref else "",
            dense=True,
        )
        secret_field = ft.TextField(
            label="Secret value (opsional, disimpan di Keychain)",
            password=True,
            can_reveal_password=True,
            dense=True,
        )
        if is_edit and ref and ref.keychain_key_name:
            existing_secret = get_secret(ref.keychain_key_name)
            if existing_secret:
                secret_field.value = existing_secret
        tags_field = ft.TextField(
            label="Tags (pisahkan dengan koma)",
            value=", ".join(ref.tags) if ref else "",
            dense=True,
        )

        def _save(e: Any) -> None:
            tags = [t.strip() for t in (tags_field.value or "").split(",") if t.strip()]
            keychain_name = (keychain_field.value or "").strip()
            pid = None
            if project_field.value and project_field.value != "":
                try:
                    pid = int(project_field.value)
                except ValueError:
                    pid = None
            if is_edit and ref:
                ref.service_name = (name_field.value or "").strip()
                ref.base_url = (url_field.value or "").strip()
                ref.description = desc_field.value or ""
                ref.auth_type = auth_field.value or ""
                ref.keychain_key_name = keychain_name
                ref.tags = tags
                ref.project_id = pid
                api_refs_repo.update_api_ref(self.conn, ref)
            else:
                api_refs_repo.create_api_ref(
                    self.conn,
                    ApiRef(
                        id=None,
                        service_name=(name_field.value or "").strip(),
                        base_url=(url_field.value or "").strip(),
                        description=desc_field.value or "",
                        auth_type=auth_field.value or "",
                        keychain_key_name=keychain_name,
                        tags=tags,
                        project_id=pid,
                    ),
                )
            if keychain_name:
                if secret_field.value:
                    store_secret(keychain_name, secret_field.value)
                else:
                    from src.core.secrets import delete_secret
                    try:
                        delete_secret(keychain_name)
                    except Exception:
                        pass
            self.page.pop_dialog()
            self.refresh()

        project_options = [ft.dropdown.Option("")]
        projects = projects_repo.list_projects(self.conn)
        for p in projects:
            project_options.append(ft.dropdown.Option(str(p.id), p.name))

        project_field = ft.Dropdown(
            label="Project",
            options=project_options,
            dense=True,
        )
        if is_edit and ref and ref.project_id:
            project_field.value = str(ref.project_id)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit API Reference" if is_edit else "Tambah API Reference"),
            content=ft.Column(
                [
                    name_field,
                    url_field,
                    desc_field,
                    auth_field,
                    keychain_field,
                    secret_field,
                    tags_field,
                    project_field,
                ],
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

    def _delete(self, ref: ApiRef) -> None:
        """Hapus api ref (dengan konfirmasi)."""

        def _confirm(e: Any) -> None:
            api_refs_repo.delete_api_ref(self.conn, ref.id)  # type: ignore[arg-type]
            self.page.pop_dialog()
            self.refresh()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Hapus API reference?"),
            content=ft.Text(f'"{ref.service_name}" akan dihapus.'),
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
    # Filter & tag
    # ------------------------------------------------------------------

    def _chip_click(self, tag: str) -> None:
        """Toggle filter by tag saat tag chip diklik."""
        if self._current_filter_tag == tag:
            self._current_filter_tag = None
        else:
            self._current_filter_tag = tag
        self._apply_filter()

    def _apply_filter(self) -> None:
        """Terapkan filter berdasarkan tag yang sedang aktif."""
        refs = api_refs_repo.list_api_refs(self.conn)
        self.list_area.controls.clear()

        if self._current_filter_tag:
            filtered = [r for r in refs if self._current_filter_tag in r.tags]
            if not filtered:
                tag = self._current_filter_tag
                msg = f"Tidak ada API dengan tag '{tag}'"
                self.list_area.controls.append(self.empty_state(msg))
            else:
                for r in filtered:
                    self.list_area.controls.append(self._item_card(r))
        else:
            if not refs:
                self.list_area.controls.append(
                    self.empty_state("Belum ada API reference. Tambahkan yang pertama!")
                )
            else:
                for r in refs:
                    self.list_area.controls.append(self._item_card(r))
        self.page.update()

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Perbarui daftar api ref di area list."""
        refs = api_refs_repo.list_api_refs(self.conn)
        self.list_area.controls.clear()

        if not refs:
            self.list_area.controls.append(
                self.empty_state("Belum ada API reference. Tambahkan yang pertama!")
            )
        else:
            for r in refs:
                self.list_area.controls.append(self._item_card(r))
        self.page.update()

    def _item_card(self, ref: ApiRef) -> ft.Container:
        """Render sederhana: service name, base URL, copy key button."""
        secret_value = get_secret(ref.keychain_key_name or ref.service_name)

        secret_display: ft.Control = ft.Container()
        if secret_value:
            secret_display = ft.Row(
                [
                    ft.Text(
                        "API Key:",
                        size=11,
                        color=PALETTE["text.secondary"],
                    ),
                    ft.Text(
                        secret_value,
                        size=12,
                        color=PALETTE["accent.mint"],
                        style=ft.TextStyle(font_family="monospace"),
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
                spacing=4,
            )

        copy_target = secret_value or ref.base_url or ref.service_name
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                ref.service_name,
                                size=16,
                                weight=ft.FontWeight.W_600,
                                color=PALETTE["text.primary"],
                            ),
                            ft.Container(expand=True),
                            _copy_btn(
                                ft.Icons.CONTENT_COPY,
                                "Copy",
                                lambda: copy_to_clipboard(
                                    self.page,
                                    copy_target,
                                    f'API key "{ref.service_name}" disalin!',
                                ),
                            ),
                            _copy_btn(
                                ft.Icons.KEY_OUTLINED,
                                "Copy key",
                                lambda: copy_to_clipboard(
                                    self.page,
                                    copy_target,
                                    f'API key "{ref.service_name}" disalin!',
                                ),
                            ),
                            _action_button(
                                ft.Icons.EDIT_OUTLINED,
                                "Edit",
                                lambda e, r=ref: self._open_edit(r),
                            ),
                            _action_button(
                                ft.Icons.DELETE_OUTLINE,
                                "Hapus",
                                lambda e, r=ref: self._delete(r),
                                danger=True,
                            ),
                        ],
                        spacing=4,
                    ),
                    ft.Text(
                        ref.base_url,
                        size=12,
                        color=PALETTE["accent.mint"],
                        style=ft.TextStyle(font_family="monospace"),
                    ),
                    secret_display,
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Text(
                                    ref.auth_type or "Tanpa auth",
                                    size=11,
                                    color=PALETTE["text.secondary"],
                                ),
                                bgcolor=PALETTE["bg.surface-hover"],
                                padding=ft.Padding.symmetric(
                                    horizontal=6, vertical=2
                                ),
                                border_radius=6,
                            ),
                            *[self._tag_chip(t) for t in ref.tags],
                        ],
                        spacing=4,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                ],
                spacing=4,
            ),
            bgcolor=PALETTE["bg.surface"],
            border=ft.Border.all(1, PALETTE["border.subtle"]),
            border_radius=8,
            padding=12,
        )

    def _tag_chip(self, tag: str) -> ft.Container:
        """Buat tag chip yang bisa diklik untuk filter."""
        is_active = self._current_filter_tag == tag
        accent = PALETTE["accent.primary"]
        surface = PALETTE["bg.surface-hover"]
        base = PALETTE["bg.base"]
        secondary = PALETTE["text.secondary"]
        chip_bg = accent if is_active else surface
        chip_fg = base if is_active else secondary
        return ft.Container(
            content=ft.Text(tag, size=11, color=chip_fg),
            bgcolor=chip_bg,
            padding=ft.Padding.symmetric(horizontal=8, vertical=2),
            border_radius=8,
            on_click=lambda e, t=tag: self._chip_click(t),
            ink=True,
        )


def _copy_btn(icon: Any, tooltip: str, on_click: Any) -> ft.IconButton:
    """Tombol salin kecil dengan warna hijau."""
    return ft.IconButton(
        icon=icon,
        icon_color=PALETTE["state.success"],
        tooltip=tooltip,
        on_click=on_click,
    )


def _action_button(
    icon: Any, tooltip: str, on_click: Any, danger: bool = False
) -> ft.IconButton:
    """Buat tombol aksi ikon kecil."""
    return ft.IconButton(
        icon=icon,
        icon_color=PALETTE["state.danger"] if danger else PALETTE["text.secondary"],
        tooltip=tooltip,
        on_click=on_click,
    )
