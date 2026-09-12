# UI MVP: Sidebar + 4 Views CRUD + Search Global — Rencana Implementasi

- **Status:** Done
- **Branch:** `feature/ui-mvp`
- **Terkait GEMINI.md bagian:** 4 (Fitur Inti v1)

## 1. Ringkasan & Tujuan

Membangun UI DevCodex: sidebar navigasi 4 modul (Labels, Prompts, Commands, API References), search global, dan 4 view dengan CRUD.

## 2. File UI yang Dibuat

```
src/app/
├── main.py                  # routing + search
├── theme.py                 # token warna
├── components/
│   └── sidebar.py           # navigasi + branding
├── views/
│   ├── base.py              # BaseView abstract
│   ├── labels_view.py       # label CRUD + segmented view
│   ├── prompts_view.py      # prompt CRUD + favorit
│   ├── commands_view.py     # command CRUD
│   └── api_refs_view.py     # API ref CRUD + Keychain
```

## 3. Definition of Done

- [x] 4 halaman bisa dibuka & CRUD lewat UI
- [x] Search global menampilkan hasil dari semua modul
- [x] UI dark mode mengikuti brand guidelines
