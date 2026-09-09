"""Helper untuk copy ke clipboard dengan pbcopy (macOS) + fallback ft.Clipboard."""

import asyncio
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import flet as ft


def copy_to_clipboard(
    page: "ft.Page", text: str, message: str = "Disalin ke clipboard!"
) -> None:
    """Salin teks ke clipboard menggunakan pbcopy (macOS) + fallback ft.Clipboard.

    Args:
        page: Objek page Flet.
        text: Teks yang akan disalin.
        message: Pesan untuk SnackBar (optional).
    """
    # Coba copy via pbcopy (macOS native)
    try:
        subprocess.run(["pbcopy"], input=text, text=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback ke ft.Clipboard jika pbcopy gagal
        async def _async_copy() -> None:
            clip = ft.Clipboard()
            page.overlay.append(clip)
            page.update()
            await clip.set(text)

        # Schedule async operation
        asyncio.create_task(_async_copy())

    # Tampilkan feedback
    snack = ft.SnackBar(ft.Text(message), bgcolor="#3DDC84")
    page.overlay.append(snack)
    snack.open = True
    page.update()
