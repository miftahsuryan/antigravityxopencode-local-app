# GEMINI.md — Konfigurasi & Instruksi Utama Agent

> File ini dibaca otomatis oleh agent Antigravity di awal setiap sesi. Ini adalah "kontrak" utama antara Anda dan agent: apa yang dibangun, dengan cara apa, dan aturan dasar apa yang tidak boleh dilanggar.
> Detail per-topik ada di `.agents/rules/*.md` — jangan duplikasi isinya di sini, cukup rujuk.

## 1. Identitas Proyek

- **Nama kerja produk:** DevCodex *(placeholder — ganti sesuai selera Anda, cukup update file ini + `docs/brand_guidelines.md`)*
- **Tujuan:** Aplikasi desktop lokal (macOS, Apple Silicon) untuk menyimpan & merekap dalam satu tempat:
  1. Catatan/dokumentasi berbasis Markdown (`.md`)
  2. Prompt AI yang sering dipakai (Claude, Gemini, GPT, dll.)
  3. Command / snippet terminal
  4. Referensi API (endpoint, deskripsi, cara auth — **bukan** gudang password)
- **Target pengguna:** Hanya untuk penggunaan pribadi (single-user), berjalan 100% lokal, tanpa akun/cloud wajib.
- **Platform:** macOS 13+ (Apple Silicon M1 Pro), dikemas sebagai aplikasi native `.app`.

## 2. Keputusan Arsitektur (Tech Stack)

| Layer | Pilihan | Alasan |
|---|---|---|
| Bahasa | Python 3.12+ | Selaras dengan basis skill yang sudah dikuasai (PEP 8) |
| UI Framework | [Flet](https://flet.dev) (berbasis Flutter) | Satu bahasa (Python) untuk UI + logic, bisa di-build jadi `.app` native M1 lewat `flet build macos`, tidak perlu belajar JS/Swift |
| Penyimpanan terstruktur | SQLite (`~/Library/Application Support/DevCodex/devcodex.db`) | File tunggal, tanpa server, gampang di-backup |
| Penyimpanan catatan | File `.md` asli di `data/vault/notes/**/*.md` | Catatan tetap portable, bisa dibuka editor lain / di-track Git terpisah kalau mau |
| Secret/API key | macOS Keychain via package `keyring` | Lihat `.agents/rules/security-and-data.md` — **jangan pernah** simpan secret mentah di SQLite/JSON |
| Testing | `pytest` + `mypy` + `ruff` + `black` | Lihat `.agents/rules/testing-and-qa.md` untuk command persis |

Alternatif yang dipertimbangkan tapi ditolak untuk v1: Electron/Tauri + React — ditolak karena menambah bahasa (JS/TS atau Rust) yang tidak selaras dengan basis Python yang sudah dikuasai, dan menambah kompleksitas build untuk kebutuhan yang sebenarnya adalah tool personal, bukan produk komersial.

## 3. Struktur Folder

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
│   └── core/              # layer logic (models, storage, search, security)
│
├── tests/                 # unit test, struktur mirror src/
├── assets/                # aset visual (icon, dll.)
└── data/                  # sample/vault lokal utk dev — DB asli di App Support (di-gitignore)
```

## 4. Fitur Inti (v1 — MVP Selesai)

1. **Notes** — CRUD catatan Markdown, folder + tag, full-text search, **copy ke clipboard**, **filter by tag**, tampilan konten penuh.
2. **Prompt Library** — simpan prompt AI, kategori per tool/model, tag, favorit/pin, **quick-copy**, **filter by tag**.
3. **Command Snippets** — simpan command terminal + deskripsi + tag, **quick-copy**, **filter by tag**.
4. **API References** — simpan nama service, base URL, deskripsi, tipe auth, tag. Secret disimpan di **macOS Keychain**, dapat di-reveal dan disalin langsung dari kartu.
5. **Cross-cutting:** global search (lintas 4 modul sekaligus), sidebar navigasi 4 section + search bar di atas, dark mode sebagai default, **filter tag pada setiap modul**, **copy to clipboard**.

Fitur yang **sengaja ditunda** ke v2+ (jangan dikerjakan tanpa diminta eksplisit): sync cloud, run-command langsung dari app, multi-user/sharing, plugin pihak ketiga.

## 5. Aturan Wajib (Rules)

Sebelum menulis kode apa pun, baca dan patuhi:
- `.agents/rules/coding-standards.md` — gaya kode, struktur modul, naming.
- `.agents/rules/testing-and-qa.md` — command wajib dijalankan tiap perubahan (self-correction loop).
- `.agents/rules/security-and-data.md` — aturan penyimpanan data & secret.
- `.agents/rules/git-workflow.md` — branch, commit message, dan kewajiban paper trail sebelum coding fitur baru.

## 6. Custom Skills

- `.agent/skills/tdd-workflow/` — alur test-driven development yang dipakai untuk logic di `core/`.
- `.agent/skills/security-review/` — checklist review sebelum kode yang menyentuh secret/API di-merge.

## 7. Alur Kerja Agent (ringkas)

1. Untuk fitur baru yang tidak trivial: buat dulu paper trail di `docs/paper-trail/` (lihat template), baru mulai coding.
2. Tulis & jalankan test sesuai `testing-and-qa.md` di setiap langkah.
3. Ikuti palet warna, tipografi, dan tone di `docs/brand_guidelines.md` untuk semua elemen UI.
4. Jangan pernah menambahkan dependency baru tanpa mencatat alasannya singkat di commit message.
