"""Helper untuk copy ke clipboard — gabungan pbcopy + ft.Clipboard."""

import subprocess

import flet as ft


def copy_to_clipboard(
    page: "ft.Page", text: str, message: str = "Disalin ke clipboard!"
) -> None:
    """Salin teks ke clipboard menggunakan pbcopy (macOS native).

    Args:
        page: Objek page Flet.
        text: Teks yang akan disalin.
        message: Pesan untuk SnackBar.
    """
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

    if copied:
        snack = ft.SnackBar(ft.Text(message), bgcolor="#3DDC84")
        page.overlay.append(snack)
        snack.open = True
        page.update()
    else:
        snack = ft.SnackBar(
            ft.Text("Gagal menyalin ke clipboard."),
            bgcolor="#F5484B",
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()
