# MVP: Labels + Prompts + Commands + API References — Rencana Implementasi

- **Status:** Done
- **Branch:** `feature/mvp-core-modules`
- **Terkait GEMINI.md bagian:** 4 (Fitur Inti v1)

## 1. Ringkasan & Tujuan

Membangun fondasi 4 modul inti DevCodex (Labels, Prompt Library, Command Snippets, API References) beserta navigasi sidebar dan search global.

## 2. Perubahan Arsitektur / Data Model

Tabel SQLite di `src/core/storage/db.py`:

- `labels(id, name [unique], color, description, created_at, updated_at)` — label dengan warna
- `label_items(id, label_id, item_type, item_id)` — junction table many-to-many
- `prompts(id, title, content, tool, is_favorite, created_at, updated_at)`
- `commands(id, title, command_text, description, created_at, updated_at)`
- `api_refs(id, service_name, base_url, description, auth_type, keychain_key_name, created_at, updated_at)`

## 3. Rencana Implementasi

1. `src/core/models.py` — dataclass: Label, Prompt, Command, ApiRef
2. `src/core/storage/db.py` — koneksi + migrasi V1
3. `src/core/storage/*_repo.py` — CRUD per entity
4. `src/core/storage/labels_repo.py` — CRUD labels + junction helpers
5. `src/core/search.py` — global search (LIKE-based)
6. `src/app/theme.py` — dark mode palette
7. `src/app/components/sidebar.py` — navigasi + search bar
8. `src/app/views/*_view.py` — 4 view modul

## 4. Rencana Pengujian

- Unit test repos: create, list, update, delete
- Unit test labels_repo: junction table operations
- Unit test search: cross-module queries
- Smoke test: buka 4 halaman, CRUD, search

## 5. Risiko & Mitigasi

- Skema DB berubah → migrasi versi dengan `PRAGMA user_version`
- API key ter-exposed → `secrets.py` wrapper `keyring`, key tidak di-export

## 6. Definition of Done

- [x] 4 modul bisa CRUD dasar
- [x] Labels dengan junction table
- [x] Search global lintas modul
- [x] UI dark mode sesuai brand guidelines
