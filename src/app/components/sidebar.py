"""Sidebar navigasi & search global.

Menampilkan branding "DevCodex", field pencarian, dan 4 tombol navigasi
modul (Notes, Prompts, Commands, API References). Mengikuti brand_guidelines.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import flet as ft

from src.app.theme import PALETTE

# Urutan & metadata navigasi modul.
MODULES: list[tuple[str, str, Any]] = [
    ("labels", "Labels", ft.Icons.LABEL_OUTLINED),
    ("prompts", "Prompts", ft.Icons.AUTO_AWESOME_OUTLINED),
    ("commands", "Commands", ft.Icons.TERMINAL_OUTLINED),
    ("api_refs", "API References", ft.Icons.CODE_OUTLINED),
]


class Sidebar:
    """Komponen sidebar: branding + search + navigasi modul."""

    def __init__(
        self,
        page: ft.Page,
        on_navigate: Callable[[str], None],
        on_search: Callable[[str], None],
    ) -> None:
        """Inisialisasi sidebar.

        Args:
            page: objek Page Flet.
            on_navigate: callback saat modul dipilih (dikirim key modul).
            on_search: callback saat query search berubah.
        """
        self.page = page
        self.on_navigate = on_navigate
        self.on_search = on_search
        self.active_key: str = "labels"
        # Simpan referensi tombol per modul untuk styling aktif.
        self._buttons: dict[str, ft.Container] = {}
        self._build()

    def _build(self) -> None:
        """Bangun child widget sidebar."""
        self.search_field = ft.TextField(
            hint_text="Cari di semua modul…",
            prefix_icon=ft.Icons.SEARCH,
            filled=True,
            dense=True,
            border_radius=8,
            on_change=lambda e: self.on_search(e.control.value or ""),
        )

        nav_buttons = ft.Column(spacing=4)
        for key, label, icon in MODULES:
            btn = self._nav_button(key, label, icon)
            self._buttons[key] = btn
            nav_buttons.controls.append(btn)

        self.root = ft.Container(
            width=240,
            bgcolor=PALETTE["bg.surface"],
            border=ft.Border.all(1, PALETTE["border.subtle"]),
            padding=16,
            content=ft.Column(
                [
                    self._branding(),
                    self.search_field,
                    ft.Divider(height=1, color=PALETTE["border.subtle"]),
                    nav_buttons,
                    ft.Container(expand=True),
                    self._footer(),
                ],
                spacing=12,
            ),
        )

    def _branding(self) -> ft.Row:
        """Baris branding: ikon + nama aplikasi."""
        return ft.Row(
            [
                ft.Container(
                    width=32,
                    height=32,
                    bgcolor=PALETTE["accent.primary"],
                    border_radius=8,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "_", color=PALETTE["bg.base"], weight=ft.FontWeight.BOLD
                    ),
                ),
                ft.Column(
                    [
                        ft.Text(
                            "DevCodex",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=PALETTE["text.primary"],
                        ),
                        ft.Text(
                            "vault dev & AI",
                            size=11,
                            color=PALETTE["text.secondary"],
                        ),
                    ],
                    spacing=0,
                ),
            ],
            spacing=10,
        )

    def _nav_button(self, key: str, label: str, icon: Any) -> ft.Container:
        """Buat tombol navigasi satu modul.

        Args:
            key: key unik modul (untuk callback).
            label: label yang ditampilkan.
            icon: ikon Flet.

        Returns:
            Container berisi tombol navigasi.
        """
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=18, color=PALETTE["text.secondary"]),
                    ft.Text(label, size=14, color=PALETTE["text.secondary"]),
                ],
                spacing=8,
            ),
            padding=8,
            border_radius=8,
            on_click=lambda _, k=key: self._select(k),
            ink=True,
        )

    def _select(self, key: str) -> None:
        """Pilih modul dan panggil callback navigasi.

        Args:
            key: key modul yang dipilih.
        """
        self.set_active(key)
        self.on_navigate(key)

    def set_active(self, key: str) -> None:
        """Tandai modul tertentu sebagai aktif (styling).

        Args:
            key: key modul aktif.
        """
        self.active_key = key
        for k, btn in self._buttons.items():
            active = k == key
            btn.bgcolor = PALETTE["accent.primary"] if active else PALETTE["bg.surface"]
            if isinstance(btn.content, ft.Row):
                for child in btn.content.controls:
                    if isinstance(child, (ft.Icon, ft.Text)):
                        child.color = (
                            PALETTE["bg.base"] if active else PALETTE["text.secondary"]
                        )

    def _footer(self) -> ft.Text:
        """Footer kecil di bawah sidebar."""
        return ft.Text(
            "v1 — lokaldir",
            size=11,
            color=PALETTE["text.secondary"],
        )

    def build(self) -> ft.Container:
        """Kembalikan container sidebar.

        Returns:
            Container utama sidebar.
        """
        return self.root
