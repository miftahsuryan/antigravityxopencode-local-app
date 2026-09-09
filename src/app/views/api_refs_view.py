"""View modul API References.

List referensi API + form modal tambah/edit + indikator secret (Keychain).
Nilai secret TIDAK pernah ditampilkan — hanya boolean status terisi/belum.
Lihat .agents/rules/security-and-data.md.
"""

from __future__ import annotations

import sqlite3
from typing import Any

import flet as ft

from src.app.theme import PALETTE
from src.app.views.base import BaseView
from src.core.models import ApiRef
from src.core.secrets import has_secret, store_secret
from src.core.storage import api_refs_repo


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
        self.refresh()

    # ------------------------------------------------------------------
    # Form & dialog
    # ------------------------------------------------------------------

    def _open_add(self) -> None:
        """Buka dialog form tambah api ref baru."""
        self._open_dialog(None)

    def _open_edit(self, ref: ApiRef) -> None:
        """Buka dialog form edit api ref.

        Args:
            ref: ApiRef yang akan diedit.
        """
        self._open_dialog(ref)

    def _open_dialog(self, ref: ApiRef | None) -> None:
        """Tampilkan modal form tambah/edit.

        Args:
            ref: ApiRef untuk mode edit, atau None untuk mode tambah.
        """
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
        tags_field = ft.TextField(
            label="Tags (pisahkan dengan koma)",
            value=", ".join(ref.tags) if ref else "",
            dense=True,
        )

        def _save(e: Any) -> None:
            tags = [t.strip() for t in (tags_field.value or "").split(",") if t.strip()]
            keychain_name = (keychain_field.value or "").strip()
            if is_edit and ref:
                ref.service_name = (name_field.value or "").strip()
                ref.base_url = (url_field.value or "").strip()
                ref.description = desc_field.value or ""
                ref.auth_type = auth_field.value or ""
                ref.keychain_key_name = keychain_name
                ref.tags = tags
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
                    ),
                )
            # Simpan secret ke Keychain kalau diisi (bukan ke DB plaintext).
            if keychain_name and secret_field.value:
                store_secret(keychain_name, secret_field.value)
            self.page.pop_dialog()
            self.refresh()

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
        """Hapus api ref (dengan konfirmasi).

        Args:
            ref: ApiRef yang akan dihapus.
        """

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
        """Render satu kartu api ref.

        Args:
            ref: ApiRef yang dirender.

        Returns:
            Container kartu api ref.
        """
        tag_chips: list[ft.Control] = [
            ft.Container(
                content=ft.Text(t, size=11, color=PALETTE["text.secondary"]),
                bgcolor=PALETTE["bg.surface-hover"],
                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                border_radius=8,
            )
            for t in ref.tags
        ]
        # Indikator secret: hanya boolean, nilai secret tidak pernah dirender.
        secret_indicator = self._secret_badge(ref)
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        ref.service_name,
                                        size=16,
                                        weight=ft.FontWeight.W_600,
                                        color=PALETTE["text.primary"],
                                    ),
                                    secret_indicator,
                                ],
                                spacing=6,
                            ),
                            ft.Text(
                                ref.base_url,
                                size=12,
                                color=PALETTE["accent.mint"],
                                style=ft.TextStyle(font_family="monospace"),
                            ),
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
                                    *tag_chips,
                                ],
                                spacing=4,
                            ),
                        ],
                        spacing=4,
                        expand=True,
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
                spacing=8,
            ),
            bgcolor=PALETTE["bg.surface"],
            border=ft.Border.all(1, PALETTE["border.subtle"]),
            border_radius=8,
            padding=12,
        )

    def _secret_badge(self, ref: ApiRef) -> ft.Container:
        """Badge status secret di Keychain (tanpa nilai).

        Args:
            ref: ApiRef yang dicek.

        Returns:
            Container badge hijau (terisi) atau abu/kuning (belum).
        """
        if not ref.keychain_key_name:
            return ft.Container()
        filled = has_secret(ref.keychain_key_name)
        color = PALETTE["state.success"] if filled else PALETTE["state.warning"]
        text = "secret ✓" if filled else "secret belum diisi"
        return ft.Container(
            content=ft.Text(text, size=11, color=color),
            border=ft.Border.all(1, color),
            padding=ft.Padding.symmetric(horizontal=6, vertical=1),
            border_radius=6,
        )


def _action_button(
    icon: Any, tooltip: str, on_click: Any, danger: bool = False
) -> ft.IconButton:
    """Buat tombol aksi ikon kecil.

    Args:
        icon: ikon Flet.
        tooltip: tooltip tombol.
        on_click: callback saat diklik.
        danger: True untuk style merah.

    Returns:
        IconButton.
    """
    return ft.IconButton(
        icon=icon,
        icon_color=PALETTE["state.danger"] if danger else PALETTE["text.secondary"],
        tooltip=tooltip,
        on_click=on_click,
    )
