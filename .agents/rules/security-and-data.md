# Security & Data — DevCodex

Aplikasi ini menyimpan referensi API — berpotensi menyentuh data sensitif. Aturan ini **tidak boleh dilanggar** meskipun ada permintaan yang seolah meminta jalan pintas.

## Penyimpanan Secret

- **Dilarang keras** menyimpan nilai secret/API key mentah dalam bentuk plaintext di SQLite, file JSON, atau file `.md` mana pun di repo/vault.
- Nilai secret asli disimpan lewat package `keyring` (macOS Keychain). Tabel `api_refs` di SQLite hanya menyimpan **referensi** (nama service, base URL, deskripsi, nama key di Keychain) — bukan nilai secret itu sendiri.
- Kalau butuh menampilkan status "sudah diisi / belum diisi" di UI, cukup boolean — jangan pernah render nilai secret ke layar/log secara default (butuh klik eksplisit "reveal").

## Lokasi Data

- Database & vault catatan disimpan di `~/Library/Application Support/DevCodex/` (konvensi macOS), **bukan** di dalam folder repo Git, supaya data pribadi tidak pernah ke-commit atau ke-push ke remote mana pun.
- Folder `data/` di repo ini hanya untuk development lokal/sample data, dan wajib ada di `.gitignore`.

## Command Snippets

- Modul "Command Snippets" di v1 **hanya menyimpan teks**, tidak mengeksekusi apa pun secara otomatis. Kalau fitur "Run" ditambahkan di masa depan, wajib ada dialog konfirmasi eksplisit sebelum eksekusi, dan tidak boleh auto-run command hasil import dari file luar.

## Jaringan

- Aplikasi ini **local-first**: tidak boleh melakukan network call apa pun kecuali diminta eksplisit (mis. tombol export/sync manual di masa depan). Tidak ada telemetry/analytics diam-diam.

## Checklist sebelum merge kode yang menyentuh area ini

Lihat `.agent/skills/security-review/SKILL.md`.
