# `core/` — Business Logic Layer

Semua logic domain: models, storage (repository pattern di atas SQLite), search, security helper (wrapper `keyring`), dan I/O (import/export JSON). Folder ini **tidak boleh** import apa pun dari `app/`.

## Struktur

```
core/
├── models.py              # dataclass: Label, Prompt, Command, ApiRef
├── storage/
│   ├── db.py              # koneksi SQLite + migrasi skema V1
│   ├── labels_repo.py     # CRUD labels + junction table helpers
│   ├── prompts_repo.py    # CRUD prompts
│   ├── commands_repo.py   # CRUD commands
│   └── api_refs_repo.py   # CRUD API references
├── search.py              # global search lintas 4 modul
├── io.py                  # export/import JSON per label
├── secrets.py             # wrapper keyring untuk macOS Keychain
└── README.md
```

## Data Models

| Model | Fields | Notes |
|---|---|---|
| `Label` | id, name (unique), color, description | Warna picker: 8 preset colors |
| `Prompt` | id, title, content, tool, is_favorite, label_ids | label_ids dari junction table |
| `Command` | id, title, command_text, description, label_ids | label_ids dari junction table |
| `ApiRef` | id, service_name, base_url, description, auth_type, keychain_key_name, label_ids | Secret disimpan di Keychain |

## Database Schema

- **Tabel:** `labels`, `prompts`, `commands`, `api_refs`, `label_items`
- **Junction table:** `label_items` untuk many-to-many Label ↔ items
- **Migrasi:** `PRAGMA user_version`, saat ini V1

## Import/Export (`io.py`)

- `export_label_to_json(conn, file_path, label_id)` — export items satu label ke JSON
- `import_label_from_json(conn, file_path)` — import dari JSON, reuse label jika sudah ada
- API key (keychain_key_name) TIDAK di-export untuk keamanan

## Menjalankan Test

```bash
pytest tests/core -q
mypy src/core/
```

## Aturan

- Repository hanya boleh tahu tabel sendiri — join di `search.py`
- Nilai secret **tidak boleh** di SQLite — gunakan `secrets.py`
- Tambah migrasi baru di `db.py`, jangan ubah skema lama tanpa paper trail
