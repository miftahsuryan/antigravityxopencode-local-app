---
name: tdd-workflow
description: Gunakan skill ini setiap kali menulis atau mengubah logic di src/core/ — memastikan alur test-driven development diikuti secara konsisten.
---

# TDD Workflow

Skill ini dipakai untuk semua perubahan logic di `src/core/` (models, storage, search, security).

## Langkah

1. **Red** — Tulis test baru di `tests/core/...` yang mendeskripsikan perilaku yang diinginkan. Jalankan `pytest -q` dan pastikan test ini **gagal** (belum ada implementasinya).
2. **Green** — Tulis kode minimal di `src/core/` supaya test tersebut lulus. Jangan tambah fitur di luar yang diminta test.
3. **Refactor** — Rapikan kode (nama, struktur, duplikasi) tanpa mengubah perilaku. Jalankan ulang seluruh test suite untuk memastikan masih hijau.
4. Jalankan urutan lengkap dari `.agents/rules/testing-and-qa.md` (black → ruff → mypy → pytest) sebelum menganggap task selesai.

## Kapan skill ini TIDAK perlu dipakai penuh

- Perubahan UI murni di `src/app/` (styling, layout) — cukup smoke test manual.
- Perubahan dokumentasi (`.md` files).

## Referensi

- `.agents/rules/testing-and-qa.md`
- `.agents/rules/coding-standards.md`
