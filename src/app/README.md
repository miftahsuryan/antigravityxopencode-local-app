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
│   └── sidebar.py        # navigasi 4 section + branding + search global
├── views/
│   ├── base.py           # helper/abstract view sederhana
│   ├── notes_view.py     # catatan bebas — full content display, copy, filter tag
│   ├── prompts_view.py   # prompt AI — copy, toggle favorit, filter tag
│   ├── commands_view.py  # command terminal — copy, filter tag
│   └── api_refs_view.py  # referensi API — reveal key, copy, filter tag
└── README.md
```

## Fitur Per Modul

| Modul | Copy | Filter Tag | Catatan |
|---|---|---|---|
| Notes | ✓ | ✓ | Tampilan catatan bebas, konten penuh |
| Prompts | ✓ | ✓ | Toggle favorit, tool/model badge |
| Commands | ✓ | ✓ | Command text display monospace |
| API References | ✓ | ✓ | Reveal API key dari Keychain |

## Menambah Halaman/Modul Baru

1. Buat file baru di `views/`, komponen reusable taruh di `components/`.
2. Ambil warna/font dari `theme.py` — jangan hardcode hex baru (lihat `../brand_guidelines.md`).
3. Panggil logic lewat fungsi dari `core/` (mis. `core.notes.search_notes(...)`), bukan akses DB langsung.
4. Jalankan smoke test manual: `python -m src.app.main`, pastikan tidak ada exception saat halaman dibuka.

## Copy & Clipboard

Semua modul memiliki tombol salin (📋) yang menggunakan `src/app/utils/clipboard.py`. Cara kerja:
1. Coba `pbcopy` (native macOS) terlebih dahulu
2. Fallback ke `ft.Clipboard()` jika pbcopy gagal
3. Tampilkan SnackBar konfirmasi

## Filter Tag

Semua modul mendukung filter tag dengan mengklik chip tag di setiap kartu. Mengklik chip yang sama akan menghapus filter.
