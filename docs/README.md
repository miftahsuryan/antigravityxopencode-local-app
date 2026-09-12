# DevCodex

Vault personal untuk menyimpan dan mengelola prompt AI, command terminal, dan referensi API dalam satu aplikasi desktop lokal (macOS).

> Status: v1.5 — Label system selesai, core features berfungsi penuh.

## Tech Stack

- Python 3.12+
- [Flet](https://flet.dev) (UI, berbasis Flutter) — dikemas ke `.app` native lewat `flet build macos`
- SQLite untuk data terstruktur
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
├── GEMINI.md              # instruksi agent
├── pyproject.toml         # konfigurasi Python project
├── requirements.txt       # dependencies
│
├── docs/                  # dokumentasi & user guides
│   ├── README.md
│   ├── brand_guidelines.md
│   ├── prompt-guide.md    # best practices menulis prompt
│   ├── command-guide.md   # reference command umum
│   └── api-reference-guide.md
│
├── src/                   # kode sumber aplikasi
│   ├── app/               # layer UI (Flet views, components, theme)
│   │   ├── main.py        # entry point, routing
│   │   ├── theme.py       # token warna/tipografi
│   │   ├── components/    # sidebar, shared cards
│   │   ├── views/         # 4 view modul (labels, prompts, commands, api_refs)
│   │   └── utils/         # clipboard helper
│   └── core/              # layer logic (models, storage, search, security)
│
├── tests/                 # unit test
└── assets/                # aset visual (icon)
```

## Fitur Utama

| Modul | Fitur |
|---|---|
| **Labels** | CRUD label dengan warna, segmented view items per label |
| **Prompts** | CRUD prompt AI, copy, favorit, label assignment, duplicate |
| **Commands** | CRUD command terminal, copy, label assignment, duplicate |
| **API References** | CRUD API refs, copy URL/key dari Keychain, label assignment, duplicate |

## Fitur Tambahan

- **Global Search** — cari lintas semua modul
- **Sorting** — urutkan berdasarkan waktu atau nama
- **Duplicate** — clone item dengan satu klik
- **Keyboard Shortcuts** — Cmd+N (new), Cmd+F (search)
- **Hover Effects** — visual feedback saat mouse hover

## Dokumentasi

- [`prompt-guide.md`](./prompt-guide.md) — best practices menulis prompt AI
- [`command-guide.md`](./command-guide.md) — reference command terminal umum
- [`api-reference-guide.md`](./api-reference-guide.md) — panduan API key management
- [`brand_guidelines.md`](./brand_guidelines.md) — identitas visual & design system
