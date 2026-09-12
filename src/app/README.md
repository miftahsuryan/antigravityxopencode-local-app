# `app/` — UI Layer

Berisi semua kode tampilan (Flet). **Tidak boleh** ada query SQL atau file I/O langsung di folder ini — semua data lewat pemanggilan fungsi/class dari `core/`.

## Struktur

```
app/
├── main.py               # entry point, routing, keyboard shortcuts, export/import
├── theme.py              # konstanta warna/tipografi dari brand_guidelines.md
├── utils/
│   └── clipboard.py      # helper copy ke clipboard (pbcopy + SnackBar feedback)
├── components/
│   ├── sidebar.py        # navigasi + branding + search + badge counters
│   ├── cards.py          # shared UI: label_chip, action_button, copy_button, build_label_checkboxes
│   └── markdown_view.py  # markdown renderer untuk preview prompt
├── views/
│   ├── base.py           # BaseView abstract class + sort dropdown
│   ├── labels_view.py    # label CRUD + segmented view (items per label)
│   ├── prompts_view.py   # prompt CRUD + favorit + markdown preview toggle
│   ├── commands_view.py  # command CRUD + monospace display
│   └── api_refs_view.py  # API ref CRUD + Keychain secret + dual copy
└── README.md
```

## Fitur Per Modul

| Modul | Copy | Labels | Duplicate | Catatan |
|---|---|---|---|---|
| Labels | — | CRUD | — | Segmented view: items grouped by label |
| Prompts | ✓ | ✓ | ✓ | Favorit, markdown preview, tool/model badge |
| Commands | ✓ | ✓ | ✓ | Monospace display |
| API References | ✓ | ✓ | ✓ | Key copy (hijau) + URL copy (abu), Keychain |

## Shared Components (`cards.py`)

- `label_chip(label)` — chip label dengan warna
- `action_button(icon, tooltip, on_click, danger)` — tombol aksi
- `copy_button(icon, tooltip, on_click, accent)` — tombol copy, `accent=True` untuk hijau (API key)
- `build_label_checkboxes(labels, current_ids)` — checkbox untuk form
- `get_selected_label_ids(checks)` — ambil ID yang dipilih
- `render_label_chips(labels)` — render baris label chips

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Cmd + N` | Tambah item baru |
| `Cmd + F` | Focus search |
| `Cmd + E` | Export data |

## Menambah Modul Baru

1. Buat file di `views/`, gunakan `BaseView` sebagai parent
2. Gunakan komponen dari `cards.py` untuk UI konsisten
3. Ambil warna dari `theme.py` — jangan hardcode hex
4. Panggil logic dari `core/` — bukan akses DB langsung
5. Tambah hover effect dengan `_hover_card(e)`
