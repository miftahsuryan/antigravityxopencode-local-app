# Git Workflow — DevCodex

## Branch Naming

- `feature/<nama-singkat>` — fitur baru
- `fix/<nama-singkat>` — perbaikan bug
- `chore/<nama-singkat>` — maintenance, dependency, tooling

## Commit Message

Format [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(prompts): tambah fitur pin/favorite untuk prompt
fix(storage): perbaiki query search yang tidak case-insensitive
docs(rules): update aturan testing
```

## Paper Trail Wajib

Untuk setiap fitur baru yang **bukan** perbaikan kecil (typo, styling minor):

1. Copy `docs/paper-trail/0000-TEMPLATE-implementation-plan.md` → `docs/paper-trail/NNNN-nama-fitur.md`.
2. Isi rencana arsitektur, langkah implementasi, dan rencana test **sebelum** mulai menulis kode.
3. Commit file rencana ini di awal branch fitur, update statusnya seiring progres.
4. Saat membuat PR, link ke file paper trail ini di deskripsi PR.

Tujuannya: memudahkan review (oleh Anda sendiri, atau kolaborator di masa depan) untuk memahami *kenapa* sebuah keputusan diambil, bukan cuma *apa* yang berubah.
