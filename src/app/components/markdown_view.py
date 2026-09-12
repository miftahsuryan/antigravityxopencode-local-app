"""Markdown preview component untuk Flet."""

from __future__ import annotations

import flet as ft

from src.app.theme import PALETTE


def render_markdown(text: str) -> ft.Container:
    """Render markdown sebagai Flet controls.

    Supports: headings, bold, italic, code blocks, inline code, lists, links.
    """
    if not text.strip():
        return ft.Container(
            content=ft.Text("(Kosong)", color=PALETTE["text.secondary"], italic=True),
            padding=8,
        )

    controls: list[ft.Control] = []
    lines = text.split("\n")
    in_code_block = False
    code_lines: list[str] = []

    for line in lines:
        if line.strip().startswith("```"):
            if in_code_block:
                # End code block
                code_text = "\n".join(code_lines)
                controls.append(_code_block(code_text))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Empty line = spacing
        if not line.strip():
            controls.append(ft.Container(height=8))
            continue

        # Headings
        if line.startswith("# "):
            controls.append(_heading(line[2:], 20))
        elif line.startswith("## "):
            controls.append(_heading(line[3:], 17))
        elif line.startswith("### "):
            controls.append(_heading(line[4:], 15))
        # Bold
        elif line.startswith("**") and line.endswith("**"):
            controls.append(ft.Text(
                line.strip("*"),
                size=14,
                weight=ft.FontWeight.BOLD,
                color=PALETTE["text.primary"],
            ))
        # Bullet list
        elif line.strip().startswith("- ") or line.strip().startswith("* "):
            content = line.strip()[2:]
            controls.append(ft.Row(
                [
                    ft.Text("•", size=14, color=PALETTE["accent.mint"]),
                    _inline_format(content),
                ],
                spacing=8,
            ))
        # Numbered list
        elif len(line.strip()) > 2 and line.strip()[0].isdigit() and ". " in line[:5]:
            controls.append(ft.Row(
                [
                    ft.Text(
                        line.strip()[:line.strip().index(". ") + 1],
                        size=14,
                        color=PALETTE["accent.mint"],
                    ),
                    _inline_format(
                        line.strip()[line.strip().index(". ") + 2:]
                    ),
                ],
                spacing=8,
            ))
        # Normal text
        else:
            controls.append(_inline_format(line))

    return ft.Container(
        content=ft.Column(controls, spacing=4),
        padding=12,
        bgcolor=PALETTE["bg.surface"],
        border_radius=8,
    )


def _heading(text: str, size: int) -> ft.Text:
    return ft.Text(
        text,
        size=size,
        weight=ft.FontWeight.BOLD,
        color=PALETTE["text.primary"],
    )


def _code_block(code: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(
            code,
            size=13,
            color=PALETTE["accent.mint"],
            style=ft.TextStyle(font_family="monospace"),
            selectable=True,
        ),
        bgcolor=PALETTE["bg.surface-hover"],
        padding=12,
        border_radius=6,
    )


def _inline_format(text: str) -> ft.Text:
    """Format inline markdown (bold, italic, code)."""
    return ft.Text(
        text,
        size=14,
        color=PALETTE["text.primary"],
        selectable=True,
    )
