# DevCodex

Vault personal untuk menyimpan dan mengelola prompt AI, command terminal, dan referensi API dalam satu aplikasi desktop lokal (macOS).

> **Status:** v2.0 — Docs module (folder system + split-pane markdown editor), markdown preview, import/export per label, hover effects, badge counters.

## Tech Stack

| Layer | Teknologi |
|---|---|
| UI | [Flet](https://flet.dev) (Flutter-based) |
| Backend | Python 3.12+ |
| Database | SQLite (WAL mode) |
| Secret | macOS Keychain via `keyring` |
| Markdown | `markdown` library |
| Testing | pytest + mypy + ruff |

## Quick Start

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run
python -m src.app.main

# Build macOS app
flet build macos
```

## Struktur Proyek

```
devcodex/
├── GEMINI.md              # instruksi agent
├── pyproject.toml         # ruff, mypy, pytest config
├── requirements.txt       # dependencies
│
├── docs/                  # dokumentasi
│   ├── README.md          # file ini
│   ├── brand_guidelines.md
│   ├── prompt-guide.md    # best practices menulis prompt
│   ├── command-guide.md   # reference command umum
│   ├── api-reference-guide.md
│   └── paper-trail/       # rencana implementasi
│
├── src/
│   ├── app/               # UI layer (Flet)
│   │   ├── main.py        # entry point, routing
│   │   ├── theme.py       # color palette
│   │   ├── components/    # sidebar, cards, markdown_view
│   │   ├── views/         # 5 module views
│   │   └── utils/         # clipboard
│   └── core/              # business logic
│       ├── models.py      # Label, Prompt, Command, ApiRef, DocFolder, DocFile
│       ├── storage/       # SQLite repos
│       ├── search.py      # global search
│       ├── io.py          # import/export JSON
│       └── secrets.py     # Keychain wrapper
│
├── tests/                 # 68 tests
└── assets/                # icon
```

## Fitur Utama

### Modul Inti

| Modul | Fitur |
|---|---|
| **Labels** | CRUD + warna + segmented view + item counts |
| **Prompts** | CRUD + copy + favorit + markdown preview + duplicate |
| **Commands** | CRUD + copy monospace + duplicate |
| **API References** | CRUD + copy URL/key + Keychain secret + duplicate |
| **Docs** | Folder tree + file manager + split-pane markdown editor + labels on folders |

### Fitur Tambahan

| Fitur | Deskripsi |
|---|---|
| **Global Search** | Cari lintas semua modul |
| **Sorting** | Newest, oldest, name A-Z, name Z-A |
| **Import/Export** | Per-label JSON export/import |
| **Keyboard Shortcuts** | Cmd+N (new), Cmd+F (search), Cmd+E (export) |
| **Hover Effects** | Visual feedback pada kartu |
| **Badge Counters** | Jumlah item di sidebar |
| **Markdown Preview** | Toggle preview pada prompt cards |

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Cmd + N` | Tambah item baru |
| `Cmd + F` | Focus search |
| `Cmd + E` | Export data |

## User Guides

| Dokumen | Deskripsi |
|---|---|
| [`prompt-guide.md`](./prompt-guide.md) | Best practices menulis prompt AI |
| [`command-guide.md`](./command-guide.md) | Reference command terminal |
| [`api-reference-guide.md`](./api-reference-guide.md) | API key management |
| [`brand_guidelines.md`](./brand_guidelines.md) | Design system & colors |

## Development

```bash
# Run tests
pytest tests/ -v

# Type check
mypy src/

# Lint
ruff check src/
```
