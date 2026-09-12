"""Shared UI components — label chips, action buttons, label checkbox builder."""

from __future__ import annotations

from typing import Any

import flet as ft

from src.app.theme import PALETTE
from src.core.models import Label


def label_chip(label: Label) -> ft.Container:
    """Chip kecil untuk menampilkan nama label dengan warnanya."""
    return ft.Container(
        content=ft.Text(label.name, size=10, color=PALETTE["bg.base"]),
        bgcolor=label.color,
        padding=ft.Padding.symmetric(horizontal=6, vertical=1),
        border_radius=4,
    )


def action_button(
    icon: Any, tooltip: str, on_click: Any, danger: bool = False
) -> ft.IconButton:
    """Tombol aksi ikon kecil untuk card actions."""
    return ft.IconButton(
        icon=icon,
        icon_color=PALETTE["state.danger"] if danger else PALETTE["text.secondary"],
        tooltip=tooltip,
        on_click=on_click,
    )


def copy_button(
    icon: Any, tooltip: str, on_click: Any, accent: bool = False
) -> ft.IconButton:
    """Tombol copy. accent=True untuk warna hijau (API key)."""
    return ft.IconButton(
        icon=icon,
        icon_color=(
            PALETTE["state.success"] if accent else PALETTE["text.secondary"]
        ),
        tooltip=tooltip,
        on_click=on_click,
    )


def build_label_checkboxes(
    all_labels: list[Label], current_label_ids: list[int]
) -> tuple[list[ft.Checkbox], ft.Control]:
    """Bangun daftar checkbox label untuk form dialog.

    Returns:
        Tuple dari (list_checkbox, column_or_text_widget).
    """
    checks: list[ft.Checkbox] = []
    for lb in all_labels:
        checks.append(
            ft.Checkbox(
                label=lb.name,
                value=lb.id in current_label_ids,
                data=lb.id,
            )
        )
    if checks:
        widget: ft.Control = ft.Column(
            controls=checks,  # type: ignore[arg-type]
            spacing=2,
            scroll=ft.ScrollMode.AUTO,
        )
    else:
        widget = ft.Text(
            "Belum ada label. Buat di halaman Labels.",
            size=12,
            color=PALETTE["text.secondary"],
        )
    return checks, widget


def get_selected_label_ids(checks: list[ft.Checkbox]) -> list[int]:
    """Ambil ID label yang dipilih dari daftar checkbox."""
    return [
        cb.data for cb in checks if cb.value  # type: ignore[attr-defined]
    ]


def render_label_chips(labels: list[Label]) -> ft.Control:
    """Render baris label chips, atau Container kosong jika kosong."""
    if labels:
        return ft.Row([label_chip(lb) for lb in labels], spacing=4)
    return ft.Container()
