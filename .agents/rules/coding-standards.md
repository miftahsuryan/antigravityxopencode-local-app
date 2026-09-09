# Coding Standards — DevCodex

Berlaku untuk seluruh kode Python di repo ini. Dirujuk dari `GEMINI.md` bagian 5.

## Gaya & Formatting

- Ikuti PEP 8. Formatter wajib: **Black** (line-length 88). Linter wajib: **Ruff**.
- Type hints wajib untuk semua fungsi/method publik (parameter & return type).
- Docstring wajib untuk semua class dan fungsi publik, format Google-style:

  ```python
  def search_notes(query: str, limit: int = 20) -> list[Note]:
      """Cari catatan berdasarkan query full-text.

      Args:
          query: kata kunci pencarian.
          limit: jumlah maksimum hasil.

      Returns:
          Daftar Note yang cocok, diurutkan berdasarkan relevansi.
      """
  ```

## Struktur & Pemisahan Layer

- `src/app/` **hanya** boleh berisi kode UI (Flet views, components, theme, navigation). Tidak boleh ada query SQL atau file I/O langsung di sini.
- `src/core/` berisi semua business logic: models, storage/repository, search, security. Tidak boleh import apa pun dari `src/app/`.
- Semua akses ke SQLite lewat repository class di `src/core/storage/`, jangan tulis SQL mentah di file lain.
- Satu file = satu tanggung jawab. Kalau sebuah file di `src/core/` sudah > ~300 baris, pertimbangkan untuk dipecah.

## Naming

- `snake_case` untuk fungsi/variabel, `PascalCase` untuk class, `UPPER_SNAKE_CASE` untuk konstanta.
- Nama modul mencerminkan domain, bukan implementasi (`core/prompts.py`, bukan `core/prompt_sqlite_helper.py`).

## Dependency

- Dependency baru harus dicatat di `requirements.txt` **dan** disebutkan alasan singkatnya di commit message.
- Hindari dependency besar untuk kebutuhan kecil (mis. jangan tambah full ORM hanya untuk 4 tabel — `sqlite3` stdlib + query helper tipis sudah cukup, kecuali kompleksitas bertambah nyata).
