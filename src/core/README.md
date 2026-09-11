# `core/` — Business Logic Layer

Semua logic domain: models, storage (repository pattern di atas SQLite), search, dan security helper (wrapper `keyring`). Folder ini **tidak boleh** import apa pun dari `app/`.

## Struktur yang disarankan

```
core/
├── models.py           # dataclass: Note (dengan content), Prompt, Command, ApiRef
├── storage/
│   ├── db.py             # koneksi SQLite + migrasi skema (V1 + V2)
│   ├── notes_repo.py
│   ├── prompts_repo.py
│   ├── commands_repo.py
│   └── api_refs_repo.py
├── search.py             # full-text search lintas 4 modul (termasuk content)
├── secrets.py             # wrapper tipis di atas `keyring`
└── README.md
```

## Migrasi Skema

Skema menggunakan `PRAGMA user_version`. Saat ini V2 (menambahkan kolom `content` ke tabel `notes`).

## Menjalankan Test Khusus Layer Ini

```bash
pytest tests/core -q
mypy core/
```

## Aturan Tambahan

- Setiap repository (`*_repo.py`) hanya boleh tahu tentang tabelnya sendiri — join lintas tabel (kalau perlu) ditaruh di `search.py`, bukan di repo individual.
- Migrasi skema: tambah versi baru di `storage/db.py`, jangan ubah skema tabel lama secara destruktif tanpa mencatatnya di paper trail terkait.
- Nilai secret **tidak boleh** disimpan di SQLite — gunakan `secrets.py` (wrapper `keyring`).
