"""Basis class untuk view modul.

Menyediakan layout header + area list + tombol tambah yang dipakai
bersama oleh 4 view modul (Notes, Prompts, Commands, API References).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import flet as ft

from src.app.theme import PALETTE


class BaseView:
    """Base class untuk semua view modul."""

    def __init__(
        self,
        page: ft.Page,
        title: str,
        icon: Any,
        on_add: Callable[[], None],
    ) -> None:
        """Inisialisasi view dasar.

        Args:
            page: objek Page Flet.
            title: judul modul.
            icon: ikon Flet untuk sidebar.
            on_add: callback saat tombol tambah diklik.
        """
        self.page = page
        self.title = title
        self.icon = icon
        self.on_add = on_add
        self.list_area = ft.Column(spacing=8)

    def header(self) -> ft.Row:
        """Buat baris header: judul + tombol tambah.

        Returns:
            Row berisi judul modul dan tombol \"+ Tambah\".
        """
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
                add_button,
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=8,
        )

    def empty_state(self, message: str) -> ft.Container:
        """Tampilkan pesan saat daftar kosong.

        Args:
            message: teks yang ditampilkan.

        Returns:
            Container dengan konten tengah.
        """
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
        """Kembalikan kontainer utama view.

        Returns:
            Container berisi header + area list.
        """
        return ft.Container(
            content=ft.Column(
                [
                    self.header(),
                    ft.Divider(height=1, color=PALETTE["border.subtle"]),
                    self.list_area,
                ],
                spacing=12,
            ),
            padding=24,
            expand=True,
        )

    def refresh(self) -> None:
        """Perbarui area list (harus dioverride oleh subclass)."""
        raise NotImplementedError("Subclass harus mengimplementasikan refresh().")
