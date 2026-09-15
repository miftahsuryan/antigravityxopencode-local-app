# GEMINI.md — Konfigurasi & Instruksi Utama Agent

> File ini dibaca otomatis oleh agent di awal setiap sesi. Ini adalah "kontrak" utama antara Anda dan agent.

## 1. Identitas Proyek

- **Nama produk:** DevCodex
- **Tujuan:** Aplikasi desktop lokal (macOS) untuk menyimpan & mengelola:
  1. Prompt AI (Claude, Gemini, GPT, dll.)
  2. Command / snippet terminal
  3. Referensi API (endpoint, auth, API key di Keychain)
  4. Dokumentasi / catatan (folder + file markdown)
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
│   ├── api-reference-guide.md
│   └── paper-trail/
├── src/
│   ├── app/               # UI layer (Flet)
│   └── core/              # business logic (models, storage, search, io)
├── tests/                 # 68 tests
└── assets/                # icon
```

## 4. Fitur Inti (v2.0)

1. **Labels** — CRUD label dengan warna, segmented view, item counts
2. **Prompts** — CRUD + copy + favorit + markdown preview + duplicate
3. **Commands** — CRUD + copy monospace + duplicate
4. **API References** — CRUD + copy URL/key + Keychain secret + duplicate
5. **Docs** — Folder tree (max 3 level) + file manager + split-pane markdown editor + label pada folder
6. **Import/Export** — per-label JSON export/import
7. **Search** — global search lintas modul
8. **Sorting** — newest, oldest, name A-Z, name Z-A
9. **Keyboard Shortcuts** — Cmd+N (new), Cmd+F (search), Cmd+E (export)
10. **Hover Effects** — visual feedback pada kartu
11. **Badge Counters** — jumlah item di sidebar

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
