# MVP: Notes + Prompts + Commands + API References — Rencana Implementasi

- **Status:** Done
- **Branch:** `feature/mvp-core-modules`
- **Terkait GEMINI.md bagian:** 4 (Fitur Inti v1)

## 1. Ringkasan & Tujuan

Membangun fondasi 4 modul inti DevCodex (Notes, Prompt Library, Command Snippets, API References) beserta navigasi sidebar dan search global, di atas skeleton yang sudah ada.

## 2. Perubahan Arsitektur / Data Model

Tabel SQLite baru di `src/core/storage/db.py`:

- `notes(id, title, file_path, tags, folder, created_at, updated_at)` — konten asli tetap di file `.md` pada `data/vault/notes/`, tabel ini hanya index.
- `prompts(id, title, content, tool, tags, is_favorite, created_at, updated_at)`
- `commands(id, title, command_text, description, tags, created_at, updated_at)`
- `api_refs(id, service_name, base_url, description, auth_type, keychain_key_name, tags, created_at, updated_at)`

## 3. Rencana Implementasi

1. `src/core/models.py` — dataclass untuk 4 entity di atas.
2. `src/core/storage/db.py` — koneksi + fungsi migrasi bikin 4 tabel kalau belum ada.
3. `src/core/storage/*_repo.py` — CRUD dasar per entity (create/list/update/delete).
4. `src/core/search.py` — full-text search sederhana (LIKE-based dulu, upgrade ke FTS5 kalau data sudah banyak).
5. `src/app/theme.py` — port token warna dari `docs/brand_guidelines.md`.
6. `src/app/components/sidebar.py` + `src/app/main.py` — navigasi 4 section + search bar.
7. `src/app/views/*_view.py` — list + form tambah/edit sederhana per modul (belum perlu fitur lanjutan seperti versioning prompt).

## 4. Rencana Pengujian

- Unit test per repository: create → list → update → delete, di `tests/core/storage/`.
- Unit test `search.py`: query yang cocok di salah satu dari 4 tabel harus muncul di hasil gabungan.
- Smoke test manual: buka tiap 4 halaman, tambah 1 data dummy di masing-masing, pastikan muncul di list & search.

## 5. Risiko & Mitigasi

- Risiko: skema DB berubah lagi setelah dipakai beberapa lama → mitigasi: mulai dengan migrasi versi sederhana (cek `PRAGMA user_version`) di `db.py` sejak awal.
- Risiko: fitur API References tergoda menyimpan key mentah untuk "sementara" → mitigasi: `src/core/secrets.py` (wrapper `keyring`) dibangun dari awal, tidak ada jalan pintas untuk skip.

## 6. Definition of Done

- [x] Semua command di `.agents/rules/testing-and-qa.md` lulus.
- [x] Checklist `.agent/skills/security-review/` terpenuhi untuk modul API References.
- [x] 4 modul bisa CRUD dasar dan muncul di search global.
- [x] UI dark mode sesuai `docs/brand_guidelines.md`.
