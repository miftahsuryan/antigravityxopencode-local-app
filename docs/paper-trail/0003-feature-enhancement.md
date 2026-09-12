# Feature Enhancement: Labels, Copy, Sort, Import/Export — Rencana Implementasi

- **Status:** Done
- **Branch:** `feature/enhancement`
- **Terkait GEMINI.md bagian:** 4 (Fitur Inti v1)

## 1. Ringkasan & Tujuan

Perubahan besar dari sistem Tags/Projects ke sistem Labels, plus penambahan fitur pendukung.

## 2. Fitur yang Diimplementasi

### v1.5 — Label System
- Ganti Projects & Tags → Labels
- Label model (name, color, description)
- Junction table `label_items` untuk many-to-many
- Segmented view di Labels view

### v1.5.1 — Foundation Cleanup
- Fix label_ids bug (tidak ter-load saat edit)
- Fix N+1 query di LabelsView
- Clean up dead migrations
- Shared UI components (`cards.py`)
- 47 tests passing

### v1.6 — Import/Export JSON
- Export per-label ke JSON
- Import dari JSON dengan label picker
- Keyboard shortcut Cmd+E

### v1.7 — Visual Polish
- Badge counters di sidebar
- Improved empty states
- Better visual hierarchy

### v1.8 — Markdown Preview
- Toggle markdown preview pada prompt cards
- Supports: headings, bold, italic, code blocks, lists
- `src/app/components/markdown_view.py`

## 3. File yang Berubah

```
src/core/
├── models.py              # Label model, project_id removed
├── storage/db.py          # Schema V1 (labels + label_items)
├── storage/labels_repo.py # CRUD + junction helpers
├── io.py                  # Export/import per-label
└── search.py              # Updated for labels

src/app/
├── main.py                # Export/import, keyboard shortcuts
├── components/
│   ├── cards.py           # Shared: label_chip, action_button, copy_button
│   ├── markdown_view.py   # Markdown renderer
│   └── sidebar.py         # Badge counters, export/import buttons
├── views/
│   ├── labels_view.py     # Label CRUD + segmented view
│   ├── prompts_view.py    # Markdown preview toggle
│   ├── commands_view.py   # Uses shared components
│   └── api_refs_view.py   # Key copy green, URL copy gray
```

## 4. Definition of Done

- [x] Labels dengan CRUD dan segmented view
- [x] Copy button berfungsi di semua modul
- [x] Import/Export per-label
- [x] Markdown preview pada prompts
- [x] Badge counters di sidebar
- [x] 47 tests passing
