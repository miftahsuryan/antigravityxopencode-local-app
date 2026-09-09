# UI MVP: Sidebar Navigasi + 4 Views CRUD + Search Global — Rencana Implementasi

- **Status:** Done
- **Branch:** `feature/ui-mvp`
- **Terkait GEMINI.md bagian:** 4 (Fitur Inti v1), docs/brand_guidelines.md

## 1. Ringkasan & Tujuan

Membangun fondasi UI DevCodex yang sudah berfungsi penuh: sidebar navigasi 4 modul (Notes, Prompts, Commands, API References), search global di atas, dan 4 halaman (view) dengan kemampuan tambah/list/edit/hapus sederhana. Terhubung langsung ke `src/core/storage/` yang sudah selesai.

Tujuan akhir: aplikasi `.app` native yang bisa dipakai untuk melakukan CRUD data dasar — sebelum nanti di-build via `flet build macos`.

## 2. Perubahan Arsitektur / Data Model

Tidak ada perubahan skema DB (masih pakai `_SCHEMA_VERSION = 1`).

File UI baru di `src/app/`:

```
src/app/
├── main.py                          # [MODIFY] scaffold UI utama + routing antar view
├── theme.py                         # sudah ada (token warna)
├── components/
│   └── sidebar.py                   # [NEW] navigasi 4 section + branding
├── views/
│   ├── base.py                      # [NEW] helper/abstract view sederhana
│   ├── notes_view.py                # [NEW]
│   ├── prompts_view.py              # [NEW]
│   ├── commands_view.py             # [NEW]
│   └── api_refs_view.py             # [NEW]
```

## 3. Rencana Implementasi (langkah)

1. `src/app/components/sidebar.py` — NavigationRail (atau custom) dengan 4 item + search field di atas.
2. `src/app/views/base.py` — basis view: container + header + list + tombol tambah.
3. `src/app/views/*_view.py` — 4 view: list item (dengan tombol edit/hapus) + form modal tambah/edit.
4. `src/app/main.py` — rakit sidebar + area konten, routing antar view, update title header.
5. Integrasi `src/core/search.py` untuk search global.

## 4. Rencana Pengujian

- Unit test: existing 27 test tetap hijau (khususnya yang menyentuh repo/search).
- Smoke test manual: buka aplikasi (`python -m src.app.main`), cek 4 halaman bisa dibuka, tambah 1 data dummy di masing-masing, pastikan muncul di list & search.

## 5. Risiko & Mitigasi

- Risiko: Flet API berubah antar versi (0.24 → 0.86).  Mitigasi: cek API yang dipakai (NavigationRail, TextField, etc.) sesuai versi terpasang.
- Risiko: UI terlalu kompleks untuk MVP.  Mitigasi: mulai dari list sederhana + modal form, tidak over-engineering.

## 6. Definition of Done

- [x] Semua command di `.agents/rules/testing-and-qa.md` lulus.
- [x] 4 halaman bisa dibuka & melakukan CRUD dasar lewat UI.
- [x] Search global menampilkan hasil dari semua modul.
- [x] UI dark mode mengikuti `docs/brand_guidelines.md`.
- [x] Paper trail ini diupdate ke status "Done".
