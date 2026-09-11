# Feature Enhancement: Copy, Filter Tag, Simplified API

- **Status:** Done
- **Branch:** `feature/enhancement`
- **Terkait GEMINI.md bagian:** 4 (Fitur Inti v1)

## 1. Ringkasan & Tujuan

Menambahkan fitur-fitur yang diperlukan untuk menjadikan DevCodex aplikasi yang sepenuhnya fungsional:

1. **Copy to Clipboard** — setiap modul (Notes, Prompts, Commands, API References) memiliki tombol salin yang menggunakan `pbcopy` (macOS native) dengan fallback `ft.Clipboard`.
2. **Filter by Tag** — setiap modul mendukung filter tag dengan klik chip tag pada setiap kartu.
3. **Simplified API References** — API key dapat di-reveal dan disalin langsung dari kartu, tanpa perlu membuka form edit.
4. **Notes Free-Form** — notes menampilkan konten penuh (tidak terpotong) dalam tampilan kartu.
5. **DB Migration V2** — menambahkan kolom `content` ke tabel `notes`.

## 2. Perubahan Arsitektur / Data Model

### DB Migration V2

- `src/core/storage/db.py` — menambahkan `_MIGRATION_V2` untuk menambahkan kolom `content` ke tabel `notes`.
- `_SCHEMA_VERSION` dinaikkan dari 1 ke 2.

### File yang Berubah

```
src/app/
├── utils/clipboard.py          # [NEW] helper copy ke clipboard
├── views/notes_view.py         # [MODIFY] full content display, copy, filter tag
├── views/prompts_view.py       # [MODIFY] filter tag, restructured card
├── views/commands_view.py      # [MODIFY] filter tag, restructured card
└── views/api_refs_view.py      # [MODIFY] reveal key, copy, filter tag

src/core/
├── storage/db.py               # [MODIFY] V2 migration, content column
├── storage/notes_repo.py       # [MODIFY] line length fix
├── models.py                   # [MODIFY] content field added to Note
└── search.py                   # [MODIFY] content column in search query
```

## 3. Rencana Implementasi

1. `src/app/utils/clipboard.py` — helper copy ke clipboard menggunakan `pbcopy` + fallback `ft.Clipboard`.
2. `src/app/views/notes_view.py` — restrukturisasi kartu, menambahkan `_tag_chip()`, `_chip_click()`, `_apply_filter()`, menampilkan full content.
3. `src/app/views/prompts_view.py` — menambahkan filter tag chip, restrukturisasi kartu.
4. `src/app/views/commands_view.py` — menambahkan filter tag chip, restrukturisasi kartu.
5. `src/app/views/api_refs_view.py` — menambahkan reveal key + copy button, filter tag chip, menghapus `_secret_badge`.
6. `src/core/storage/db.py` — menambahkan kolom `content` ke tabel `notes` via V2 migration.
7. `src/core/models.py` — menambahkan `content: str = ""` ke dataclass `Note`.

## 4. Rencana Pengujian

- **Lint:** `ruff check src/` — semua file harus linter-free.
- **Type check:** `mypy src/` — semua file harus type-safe.
- **Smoke test manual:**
  1. Buka aplikasi (`python -m src.app.main`).
  2. Tambah note, pastikan konten ditampilkan penuh.
  3. Klik tombol salin (📋) pada catatan, pastikan konten tersalin.
  4. Klik chip tag pada catatan, pastikan filter bekerja.
  5. Buka tab API References, tambah API dengan key, klik "Reveal key", pastikan key muncul.
  6. Klik copy button, pastikan API key tersalin ke clipboard.
  7. Klik chip tag, pastikan filter bekerja.

## 5. Risiko & Mitigasi

- Risiko: `pbcopy` tidak tersedia di non-macOS → mitigasi: fallback `ft.Clipboard` sudah tersedia.
- Risiko: DB migration gagal pada database lama → mitigasi: `CREATE TABLE IF NOT EXISTS` dan `ALTER TABLE` sudah digunakan, migrasi versi diperiksa dengan `PRAGMA user_version`.
- Risiko: `ft.Clipboard` tidak bekerja di beberapa platform → mitigasi: `pbcopy` sebagai primary, `ft.Clipboard` sebagai fallback.

## 6. Definition of Done

- [x] Semua perintah `ruff check src/` lulus.
- [x] Semua perintah `mypy src/` lulus.
- [x] Copy button berfungsi di semua 4 modul (Notes, Prompts, Commands, API References).
- [x] Filter by tag berfungsi di semua 4 modul.
- [x] API References menampilkan dan menyalin API key langsung dari kartu.
- [x] Notes menampilkan konten penuh (tidak terpotong).
- [x] DB migration V2 berjalan lancar.
