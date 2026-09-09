# Testing & QA — DevCodex

Ini adalah "bahan bakar" self-correction loop agent. **Setiap** perubahan kode — sekecil apa pun — wajib melewati urutan berikut sebelum dianggap selesai:

```bash
# 1. Format otomatis
black .

# 2. Lint (auto-fix yang bisa)
ruff check --fix .

# 3. Type check
mypy src/core/ src/app/

# 4. Unit test
pytest -q
```

## Aturan

- Agent **tidak boleh** melaporkan sebuah task selesai kalau salah satu dari 4 command di atas gagal atau belum dijalankan. Tampilkan output command tersebut sebagai bukti.
- Setiap fungsi publik baru di `core/` wajib punya minimal 1 unit test di `tests/core/` (mirror struktur folder `core/`).
- Test untuk `app/` (UI) cukup smoke test dasar (halaman bisa dibuka tanpa exception) — jangan over-engineer test UI di v1.
- Kalau sebuah bug ditemukan: tulis dulu test yang mereproduksi bug tersebut (harus gagal/red), baru perbaiki kode sampai test hijau. Lihat skill `.agent/skills/tdd-workflow/`.
- Target coverage `core/` (logic layer): usahakan >80%, tapi jangan tulis test palsu hanya untuk mengejar angka — coverage rendah yang jujur lebih baik daripada test yang tidak menguji apa pun.

## Menjalankan Aplikasi untuk Smoke Test Manual

```bash
python -m app.main
```

Kalau ada perubahan besar di navigasi/struktur UI, jalankan ini secara manual dan screenshot hasilnya sebelum minta review manusia.
