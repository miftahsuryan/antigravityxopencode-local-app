"""Helper untuk copy ke clipboard — gabungan pbcopy + ft.Clipboard."""

import subprocess
from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    pass

# Snackbar singleton — di-reuse untuk menghindari memory leak.
_snack: ft.SnackBar | None = None


def copy_to_clipboard(
    page: "ft.Page", text: str, message: str = "Disalin ke clipboard!"
) -> None:
    """Salin teks ke clipboard menggunakan pbcopy (macOS native).

    Args:
        page: Objek page Flet.
        text: Teks yang akan disalin.
        message: Pesan untuk SnackBar.
    """
    global _snack
    copied = False
    try:
        subprocess.run(
            ["pbcopy"],
            input=text.encode("utf-8"),
            check=True,
            timeout=5,
        )
        copied = True
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        copied = False

    if _snack is None:
        _snack = ft.SnackBar(ft.Text(""), bgcolor="#3DDC84")
        page.overlay.append(_snack)

    if copied:
        _snack.content = ft.Text(message)
        _snack.bgcolor = "#3DDC84"
    else:
        _snack.content = ft.Text("Gagal menyalin ke clipboard.")
        _snack.bgcolor = "#F5484B"

    _snack.open = True
    page.update()
