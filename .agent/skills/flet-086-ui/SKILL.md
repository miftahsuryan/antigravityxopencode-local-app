---
name: flet-086-ui
description: Cheatsheet API Flet 0.86 yang terbukti bekerja di DevCodex. Gunakan setiap kali menulis/mengubah UI di src/app/ untuk menghindari error karena perbedaan API dengan versi Flet lama atau dokumentasi online.
---

# Flet 0.86 — API Cheatsheet (terbukti bekerja)

Versi Flet yang terinstall di proyek ini adalah **0.86.5**. Banyak API **berbeda** dari versi lama (`>=0.24`) dan dari dokumentasi online umum. Gunakan panduan ini untuk menghindari menebak-nebak.

## Ikon

Gunakan `ft.Icons.XXX` (huruf besar `I`), **bukan** `ft.icons.xxx`.

```python
ft.Icons.DESCRIPTION_OUTLINED
ft.Icons.STAR
ft.Icons.INBOX
```

## Layout helpers — TIDAK ada module helper lama

- **Border:** `ft.Border.all(width, color)` — bukan `ft.border.all(...)`.
- **Padding:** `ft.Padding.all(value)` / `ft.Padding.symmetric(horizontal=…, vertical=…)` — bukan `ft.padding.*`.
- **Alignment:** `ft.Alignment(0, 0)` untuk center — bukan `ft.alignment.center`.

```python
ft.Container(
    border=ft.Border.all(1, PALETTE["border.subtle"]),
    padding=ft.Padding.symmetric(horizontal=8, vertical=2),
)
```

## Dialog & Overlay

```python
# Buka dialog
page.show_dialog(dialog)      # bukan page.open(...)
# Tutup dialog
page.pop_dialog()             # bukan page.close(...)

# SnackBar: tambah ke overlay, set open, lalu update
snack = ft.SnackBar(ft.Text("..."), bgcolor=PALETTE["state.success"])
page.overlay.append(snack)
snack.open = True
page.update()
```

## Clipboard

`page.clipboard` adalah property **read-only** — tidak bisa di-set.

Gunakan `ft.Clipboard()` dan `await clip.set(text)` (async):

```python
async def _copy(...) -> None:
    clip = ft.Clipboard()
    page.overlay.append(clip)
    page.update()
    await clip.set(text)          # WAJIB await (coroutine)
```

Karena `set` mengembalikan coroutine, handler-nya harus `async def`.

## Tipografi

```python
# Semi-bold: tidak ada SEMI_BOLD
weight=ft.FontWeight.W_600

# Monospace di TextField: gunakan text_style, bukan style=
ft.TextField(text_style=ft.TextStyle(font_family="monospace"))
```

## Entry point

```python
if __name__ == "__main__":
    ft.run(main)          # modern; ft.app(...) deprecated sejak 0.80
```

## Type hints (tips mypy)

- `ft.Icons.XXX` bertipe `IconData`, bukan `str`.
- Parameter ikon & callback `on_click`/`on_change` → annotasikan sebagai `Any` agar tidak memicu error mypy yang ribet.

```python
from typing import Any

def _action_button(icon: Any, tooltip: str, on_click: Any, danger: bool = False) -> ft.IconButton:
    return ft.IconButton(icon=icon, tooltip=tooltip, on_click=on_click)
```

## Referensi

- `src/app/views/*.py` — contoh penerapan yang sudah lulus QA (black, ruff, mypy, pytest).
