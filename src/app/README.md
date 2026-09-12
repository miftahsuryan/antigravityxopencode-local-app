# `app/` — UI Layer

Berisi semua kode tampilan (Flet). **Tidak boleh** ada query SQL atau file I/O langsung di folder ini — semua data lewat pemanggilan fungsi/class dari `core/`.

## Struktur

```
app/
├── main.py               # entry point, setup Flet Page, routing antar view
├── theme.py              # konstanta warna/tipografi dari brand_guidelines.md
├── utils/
│   └── clipboard.py      # helper copy ke clipboard (pbcopy + ft.Clipboard fallback)
├── components/
│   ├── sidebar.py        # navigasi 4 section + branding + search global
│   └── cards.py          # shared UI: label_chip, action_button, copy_button, build_label_checkboxes
├── views/
│   ├── base.py           # helper/abstract view sederhana
│   ├── labels_view.py    # label management + segmented view
│   ├── prompts_view.py   # prompt AI — copy, toggle favorit, label assignment
│   ├── commands_view.py  # command terminal — copy, label assignment
│   └── api_refs_view.py  # referensi API — reveal key, copy, label assignment
└── README.md
```

## Fitur Per Modul

| Modul | Copy | Labels | Catatan |
|---|---|---|---|
| Labels | — | CRUD | Segmented view: items grouped by label |
| Prompts | ✓ | ✓ | Toggle favorit, tool/model badge, duplicate |
| Commands | ✓ | ✓ | Command text display monospace, duplicate |
| API References | ✓ | ✓ | Reveal API key dari Keychain, dual copy (URL + key), duplicate |

## Shared Components (`cards.py`)

Semua komponen reusable diekstrak ke `cards.py`:
- `label_chip(label)` — chip kecil untuk menampilkan label
- `action_button(icon, tooltip, on_click, danger)` — tombol aksi ikon
- `copy_button(icon, tooltip, on_click)` — tombol copy dengan warna hijau
- `build_label_checkboxes(labels, current_ids)` — bangun checkbox untuk form
- `get_selected_label_ids(checks)` — ambil ID yang dipilih
- `render_label_chips(labels)` — render baris label chips

## Menambah Halaman/Modul Baru

1. Buat file baru di `views/`, gunakan `BaseView` sebagai parent class
2. Gunakan komponen dari `cards.py` untuk UI yang konsisten
3. Ambil warna/font dari `theme.py` — jangan hardcode hex baru
4. Panggil logic lewat fungsi dari `core/` — bukan akses DB langsung
5. Tambahkan hover effect dengan `_hover_card(e)` function
