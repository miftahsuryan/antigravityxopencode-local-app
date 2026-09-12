# v1.8: Markdown Preview + Hover Effects + Badge Counters

- **Status:** Done
- **Branch:** `feature/markdown-preview`
- **Terkait GEMINI.md bagian:** 4 (Fitur Inti v1)

## 1. Ringkasan & Tujuan

Menambahkan fitur visual dan produktivitas: markdown preview, hover effects, badge counters, dan shared components.

## 2. Fitur yang Diimplementasi

### Markdown Preview (`src/app/components/markdown_view.py`)
- Renderer markdown sederhana untuk Flet
- Supports: headings (h1-h3), bold, italic, code blocks, bullet lists, numbered lists
- Toggle button (eye icon) pada prompt cards

### Hover Effects
- Semua kartu (prompts, commands, api_refs) memiliki hover effect
- Background berubah ke `bg.surface-hover` saat mouse hover

### Badge Counters
- Sidebar menampilkan jumlah item per modul
- Badge update otomatis saat navigasi

### Shared Components (`src/app/components/cards.py`)
- `label_chip(label)` — chip label dengan warna
- `action_button(icon, tooltip, on_click, danger)` — tombol aksi
- `copy_button(icon, tooltip, on_click, accent)` — tombol copy, `accent=True` untuk hijau
- `build_label_checkboxes(labels, current_ids)` — checkbox untuk form
- `get_selected_label_ids(checks)` — ambil ID yang dipilih
- `render_label_chips(labels)` — render baris label chips

### Import/Export Per-Label
- Export: pilih label → export items ke `devcodex_{label_name}.json`
- Import: pilih file → import items, reuses existing label
- API key (keychain_key_name) TIDAK di-export

## 3. Definition of Done

- [x] Markdown preview toggle berfungsi
- [x] Hover effects berfungsi di semua kartu
- [x] Badge counters update otomatis
- [x] Import/Export per-label berfungsi
- [x] API key tidak di-export
- [x] Copy button: abu untuk text, hijau untuk API key
- [x] 47 tests passing
