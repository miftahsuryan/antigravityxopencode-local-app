# DevCodex

Vault personal untuk merekap catatan Markdown, prompt AI, command terminal, dan referensi API dalam satu aplikasi desktop lokal (macOS, Apple Silicon).

> Status: starter scaffold — dibuat untuk dikembangkan lebih lanjut lewat agent di Antigravity IDE. Lihat [`GEMINI.md`](../GEMINI.md) untuk spesifikasi & aturan lengkap.

## Tech Stack

- Python 3.12+
- [Flet](https://flet.dev) (UI, berbasis Flutter) — dikemas ke `.app` native lewat `flet build macos`
- SQLite untuk data terstruktur, file `.md` asli untuk catatan
- `keyring` untuk penyimpanan secret di macOS Keychain

## Setup Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# jalankan versi development
python -m src.app.main
```

## Build Aplikasi Native (macOS, Apple Silicon)

```bash
flet build macos
```

Output `.app` akan ada di folder `build/macos/`.

## Struktur Proyek

| Folder | Isi |
|---|---|
| `src/app/` | UI (views, components, theme) — lihat `src/app/README.md` |
| `src/core/` | Business logic (models, storage, search) — lihat `src/core/README.md` |
| `tests/` | Unit test, struktur mirror `src/app/` & `src/core/` |
| `docs/paper-trail/` | Rencana implementasi per fitur |
| `.agents/rules/` | Aturan tim untuk agent AI |
| `.agent/skills/` | Custom skill untuk agent AI |
| `docs/` | Dokumentasi & brand guidelines |

## Dokumen Penting untuk Agent AI

- [`GEMINI.md`](../GEMINI.md) — spesifikasi & instruksi utama
- [`brand_guidelines.md`](./brand_guidelines.md) — identitas visual
- [`.agents/rules/`](../.agents/rules/) — standar kode, testing, keamanan, git workflow
