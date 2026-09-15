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
    ("docs", "Docs", ft.Icons.DESCRIPTION_OUTLINED),
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
        self._buttons: dict[str, ft.Container] = {}
        self._badges: dict[str, ft.Container] = {}
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
        """Buat tombol navigasi satu modul dengan badge counter."""
        badge = ft.Container(
            content=ft.Text("", size=10, color=PALETTE["text.secondary"]),
            bgcolor=PALETTE["bg.surface-hover"],
            padding=ft.Padding.symmetric(horizontal=6, vertical=1),
            border_radius=8,
            visible=False,
        )
        self._badges[key] = badge
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=18, color=PALETTE["text.secondary"]),
                    ft.Text(label, size=14, color=PALETTE["text.secondary"]),
                    ft.Container(expand=True),
                    badge,
                ],
                spacing=8,
            ),
            padding=8,
            border_radius=8,
            on_click=lambda _, k=key: self._select(k),
            ink=True,
        )

    def update_badge(self, key: str, count: int) -> None:
        """Update badge counter untuk modul tertentu."""
        if key in self._badges:
            badge = self._badges[key]
            if count > 0:
                badge.content = ft.Text(
                    str(count), size=10, color=PALETTE["text.secondary"]
                )
                badge.visible = True
            else:
                badge.visible = False
            self.page.update()

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

    def _footer(self) -> ft.Row:
        """Footer dengan tombol export/import."""
        export_btn = ft.IconButton(
            icon=ft.Icons.UPLOAD_FILE,
            icon_color=PALETTE["text.secondary"],
            icon_size=16,
            tooltip="Export data",
            on_click=lambda e: (
                self._on_export() if hasattr(self, '_on_export') else None
            ),
        )
        import_btn = ft.IconButton(
            icon=ft.Icons.DOWNLOAD,
            icon_color=PALETTE["text.secondary"],
            icon_size=16,
            tooltip="Import data",
            on_click=lambda e: (
                self._on_import() if hasattr(self, '_on_import') else None
            ),
        )
        return ft.Row(
            [
                ft.Text(
                    "v2.0",
                    size=11,
                    color=PALETTE["text.secondary"],
                ),
                ft.Container(expand=True),
                export_btn,
                import_btn,
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.END,
        )

    def set_export_import_handlers(
        self, on_export: Any, on_import: Any
    ) -> None:
        """Set callback untuk export/import."""
        self._on_export = on_export
        self._on_import = on_import

    def build(self) -> ft.Container:
        """Kembalikan container sidebar.

        Returns:
            Container utama sidebar.
        """
        return self.root
