# DevCodex

Vault personal untuk merekap catatan Markdown, prompt AI, command terminal, dan referensi API dalam satu aplikasi desktop lokal (macOS, Apple Silicon).

> Status: v1 MVP selesai. Aplikasi bisa menjalankan CRUD dasar, filter tag, dan copy ke clipboard di semua modul.

## Tech Stack

- Python 3.12+
- [Flet](https://flet.dev) (UI, berbasis Flutter) — dikemas ke `.app` native lewat `flet build macos`
- SQLite untuk data terstruktur (terletak di `~/Library/Application Support/DevCodex/devcodex.db`)
- `keyring` untuk penyimpanan secret di macOS Keychain
- `pytest` + `mypy` + `ruff` untuk testing & code quality

## Setup Development

```bash
# Buat virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Jalankan versi development
python -m src.app.main
```

## Build Aplikasi Native (macOS)

```bash
# Pastikan flet terinstall
pip install flet

# Build macOS .app bundle
flet build macos
```

Output `.app` akan ada di folder `build/macos/`.

## Struktur Proyek

```
devcodex/
├── GEMINI.md              # instruksi agent (auto-discovery)
├── .agents/rules/         # aturan tim & QA
├── .agent/skills/         # custom skills
├── pyproject.toml         # konfigurasi Python project
├── requirements.txt       # dependencies
│
├── docs/                  # dokumentasi & brand guidelines
│   ├── README.md
│   ├── brand_guidelines.md
│   └── paper-trail/       # rencana implementasi per fitur
│
├── src/                   # kode sumber aplikasi
│   ├── app/               # layer UI (Flet views, components, theme)
│   │   ├── main.py        # entry point, routing
│   │   ├── theme.py       # token warna/tipografi
│   │   ├── components/    # sidebar, komponen reusable
│   │   ├── views/         # 4 view modul (notes, prompts, commands, api_refs)
│   │   └── utils/         # clipboard helper
│   └── core/              # layer logic (models, storage, search, security)
│
├── tests/                 # unit test, struktur mirror src/
├── assets/                # aset visual (icon, dll.)
└── data/                  # sample/vault lokal utk dev — DB asli di App Support
```

## Fitur Utama

| Modul | Fitur |
|---|---|
| **Notes** | CRUD catatan bebas, copy konten, filter by tag |
| **Prompts** | CRUD prompt AI, toggle favorit, copy, filter by tag |
| **Commands** | CRUD command terminal, copy, filter by tag |
| **API References** | CRUD API refs, reveal/copy key dari Keychain, filter by tag |

## Dokumen Penting

- [`GEMINI.md`](../GEMINI.md) — spesifikasi & instruksi utama
- [`brand_guidelines.md`](./brand_guidelines.md) — identitas visual
- [`.agents/rules/`](../.agents/rules/) — standar kode, testing, keamanan, git workflow
- [`paper-trail/`](./paper-trail/) — rencana & dokumentasi perubahan fitur
