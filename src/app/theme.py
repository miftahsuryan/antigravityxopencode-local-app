"""Token tema (warna/tipografi) — sumber tunggal, rujuk brand_guidelines.md.

Jangan hardcode warna baru di luar file ini.
"""

from __future__ import annotations

PALETTE: dict[str, str] = {
    "bg.base": "#0E0F12",
    "bg.surface": "#17181D",
    "bg.surface-hover": "#1F2126",
    "text.primary": "#EDEEF0",
    "text.secondary": "#9A9CA5",
    "accent.primary": "#6C8CFF",
    "accent.mint": "#2DD4BF",
    "state.success": "#3DDC84",
    "state.warning": "#F5A623",
    "state.danger": "#F5484B",
    "border.subtle": "#26282F",
}

FONT_UI = "-apple-system"
FONT_CONTENT = "Inter"
FONT_MONO = "JetBrains Mono"
