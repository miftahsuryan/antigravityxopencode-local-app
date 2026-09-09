---
name: security-review
description: Checklist wajib sebelum kode yang menyentuh secret, API reference, atau penyimpanan data di-merge/dianggap selesai.
---

# Security Review Checklist

Jalankan checklist ini setiap kali perubahan menyentuh: modul API References, package `keyring`, atau lapisan storage (`src/core/storage/`).

- [ ] Tidak ada nilai secret/API key mentah tertulis langsung di kode, test, atau file `.md` mana pun.
- [ ] Nilai secret hanya lewat `keyring.set_password(...)` / `keyring.get_password(...)`, tidak pernah lewat `print()`, log, atau disimpan ke SQLite/JSON.
- [ ] Tabel `api_refs` di database hanya berisi metadata (nama service, base URL, deskripsi, nama key Keychain) — cek ulang skema kalau ada kolom baru yang berpotensi menyimpan nilai mentah.
- [ ] Field secret di UI default tersembunyi (mis. `••••••••`), butuh aksi eksplisit user untuk "reveal".
- [ ] Tidak ada network call baru yang tidak diminta eksplisit (lihat `.agents/rules/security-and-data.md`).
- [ ] `data/` (folder dev lokal) tetap ada di `.gitignore` — pastikan tidak ada file data pribadi yang ikut ter-stage di `git add`.

Kalau salah satu poin di atas tidak terpenuhi, **jangan** lanjut merge — perbaiki dulu, atau tandai eksplisit di paper trail terkait kenapa itu perlu pengecualian.
