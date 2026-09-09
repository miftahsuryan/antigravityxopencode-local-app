# `app/` — UI Layer

Berisi semua kode tampilan (Flet). **Tidak boleh** ada query SQL atau file I/O langsung di folder ini — semua data lewat pemanggilan fungsi/class dari `core/`.

## Struktur yang disarankan

```
app/
├── main.py            # entry point, setup Flet Page, routing
├── theme.py            # konstanta warna/tipografi dari brand_guidelines.md
├── views/
│   ├── notes_view.py
│   ├── prompts_view.py
│   ├── commands_view.py
│   └── api_refs_view.py
├── components/
│   ├── sidebar.py
│   ├── search_bar.py
│   └── copy_button.py
└── README.md
```

## Menambah Halaman/Modul Baru

1. Buat file baru di `views/`, komponen reusable taruh di `components/`.
2. Ambil warna/font dari `theme.py` — jangan hardcode hex baru (lihat `../brand_guidelines.md`).
3. Panggil logic lewat fungsi dari `core/` (mis. `core.notes.search_notes(...)`), bukan akses DB langsung.
4. Jalankan smoke test manual: `python -m app.main`, pastikan tidak ada exception saat halaman dibuka.
