# Brand Guidelines — DevCodex

> Placeholder brand kit. Ganti nama, warna, atau tone sesuai selera — tapi begitu diubah di sini, harus konsisten dipakai di semua layar oleh agent.

## 1. Identitas

- **Nama:** DevCodex
- **Tagline:** "Satu tempat untuk semua konteks dev & AI Anda."
- **Positioning:** Vault personal yang cepat, tenang, dan tidak mengganggu — bukan aplikasi produktivitas yang ramai dengan notifikasi.

## 2. Tone of Voice

- Teknis, ringkas, langsung ke inti — hindari bahasa marketing/hype.
- Microcopy pakai istilah yang familiar untuk developer (mis. "Copy", "Run", "Tag" — bukan padanan Indonesia yang kaku).
- Pesan error harus actionable: sebutkan apa yang salah + langkah berikutnya, bukan sekadar "Terjadi kesalahan."

## 3. Palet Warna

Dark mode adalah tampilan **default** (target pengguna developer, dipakai lama di depan layar).

| Token | Dark | Light | Pemakaian |
|---|---|---|---|
| `bg.base` | `#0E0F12` | `#FAFAFA` | Background utama |
| `bg.surface` | `#17181D` | `#FFFFFF` | Card, sidebar, modal |
| `bg.surface-hover` | `#1F2126` | `#F0F0F2` | Hover state |
| `text.primary` | `#EDEEF0` | `#15161A` | Teks utama |
| `text.secondary` | `#9A9CA5` | `#6B6D76` | Teks sekunder/meta |
| `accent.primary` | `#6C8CFF` | `#4A63D6` | Aksi utama, link, ikon aktif |
| `accent.mint` | `#2DD4BF` | `#0FA895` | Highlight modul "Prompt" |
| `state.success` | `#3DDC84` | `#1E9E56` | Sukses, konfirmasi |
| `state.warning` | `#F5A623` | `#B97300` | Peringatan (mis. secret belum di-set) |
| `state.danger` | `#F5484B` | `#C62828` | Hapus, error |
| `border.subtle` | `#26282F` | `#E4E4E7` | Garis pemisah tipis |

## 4. Tipografi

- **UI chrome (menu, tombol, label):** San Francisco / system font macOS (`-apple-system`) — supaya terasa native.
- **Konten & catatan:** Inter — untuk teks panjang di editor Markdown.
- **Kode, command, prompt, output:** JetBrains Mono atau SF Mono — wajib untuk semua blok command/kode.
- Skala ukuran: 12 / 14 / 16 / 20 / 24 / 32 px. Line-height konten teks = 1.5.

## 5. Ikonografi & Bentuk

- Gaya ikon: line icon, stroke 1.5–2px, bukan ikon solid/filled.
- Radius sudut: 8px untuk card/tombol kecil, 12px untuk modal/panel besar.
- Spacing scale (px): 4, 8, 12, 16, 24, 32, 48 — jangan pakai nilai di luar skala ini tanpa alasan.
- Shadow dipakai tipis saja (elevation rendah) — hindari efek mengambang berlebihan, sesuai nuansa "tenang, tidak ramai".

## 6. Logo (konsep awal)

Konsep: bracket terminal `>_` di dalam bentuk vault/folder membulat, warna `accent.primary` di atas `bg.surface`. Lihat `assets/icon.svg` sebagai starting point yang bisa diiterasi lebih lanjut.

## 7. Aturan untuk Agent Frontend

- Semua warna WAJIB diambil dari token di atas (bukan hex baru di tengah kode) — didefinisikan sebagai theme constants di `app/theme.py`.
- Setiap layar baru default mengikuti dark palette; light mode adalah toggle opsional, bukan prioritas v1.
- Semua blok command/prompt/kode di UI wajib pakai font monospace + tombol "Copy" di pojoknya.
