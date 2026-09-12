# GEMINI.md — Konfigurasi & Instruksi Utama Agent

> File ini dibaca otomatis oleh agent di awal setiap sesi. Ini adalah "kontrak" utama antara Anda dan agent.

## 1. Identitas Proyek

- **Nama produk:** DevCodex
- **Tujuan:** Aplikasi desktop lokal (macOS) untuk menyimpan & mengelola:
  1. Prompt AI (Claude, Gemini, GPT, dll.)
  2. Command / snippet terminal
  3. Referensi API (endpoint, auth, API key di Keychain)
- **Target pengguna:** Single-user, 100% lokal, tanpa cloud
- **Platform:** macOS 13+ (Apple Silicon), `.app` native

## 2. Tech Stack

| Layer | Pilihan |
|---|---|
| UI | [Flet](https://flet.dev) (Flutter-based) |
| Bahasa | Python 3.12+ |
| Database | SQLite (WAL mode, `~/Library/Application Support/DevCodex/devcodex.db`) |
| Secret | macOS Keychain via `keyring` |
| Markdown | `markdown` library |
| Testing | pytest + mypy + ruff |

## 3. Struktur Folder

```
devcodex/
├── GEMINI.md              # file ini
├── pyproject.toml         # ruff, mypy, pytest config
├── requirements.txt       # dependencies
├── docs/                  # dokumentasi & user guides
│   ├── README.md
│   ├── brand_guidelines.md
│   ├── prompt-guide.md
│   ├── command-guide.md
│   └── api-reference-guide.md
├── src/
│   ├── app/               # UI layer (Flet)
│   └── core/              # business logic (models, storage, search, io)
├── tests/                 # 47 tests
└── assets/                # icon
```

## 4. Fitur Inti (v1.8)

1. **Labels** — CRUD label dengan warna, segmented view, item counts
2. **Prompts** — CRUD + copy + favorit + markdown preview + duplicate
3. **Commands** — CRUD + copy monospace + duplicate
4. **API References** — CRUD + copy URL/key + Keychain secret + duplicate
5. **Import/Export** — per-label JSON export/import
6. **Search** — global search lintas modul
7. **Sorting** — newest, oldest, name A-Z, name Z-A
8. **Keyboard Shortcuts** — Cmd+N (new), Cmd+F (search), Cmd+E (export)
9. **Hover Effects** — visual feedback pada kartu
10. **Badge Counters** — jumlah item di sidebar

Fitur yang **ditunda** ke v2+: command runner, AI model integration, prompt templates, version history, bulk actions, workflow builder.

## 5. Aturan Wajib

- Ruff, mypy, dan pytest harus lulus sebelum commit
- Secret tidak boleh di-export atau disimpan di SQLite
- Gunakan `PALETTE` dari `theme.py`, jangan hardcode warna
- Ikuti PEP 8 dan coding standards yang ada
- Buat paper trail sebelum implementasi fitur baru

## 6. Testing

```bash
pytest tests/ -v          # run all tests
ruff check src/           # lint
mypy src/                 # type check
```

## 7. Build

```bash
flet build macos          # build .app bundle
```
