# Asisten Madrasah

**AI assistant madrasah yang aman & terpercaya.**

Asisten Madrasah adalah agent AI untuk MTsN 1 Jakarta yang menjawab pertanyaan akademik dan
administrasi untuk **7 peran berbeda** — dengan 5 pilar akuntabilitas: selalu menyebut sumber,
patuh pada batas kewenangan, minta persetujuan sebelum bertindak, mengakui kalau tidak tahu,
dan mencatat seluruh interaksi di audit trail.

Dibangun sebagai **Expert Package** di [Tencent Cloud WorkBuddy](https://www.workbuddy.ai)
untuk **AI CAN DO IT — Tencent Cloud Hackathon Indonesia 2026**:
Challenge A (*The Workplace Brain*) + bonus Challenge B (*Smart Task Handler*).

[**Coba demo hidup**](https://asisten-madrasah-demo.apps.workbuddy.host/index.html?sharecode=U52RKMFPEM)
— 23 skenario, 7 peran, panel pipeline dan audit yang bisa ditelusuri sendiri.

---

## Kenapa ini berbeda

Agent ini **bukan sekadar menjawab pertanyaan**. Yang membuatnya berbeda adalah urutan
pemrosesannya:

- **L4 (Permission Check) berjalan sebelum L5 (Retrieval).** Penolakan terjadi sebelum satu
  dokumen pun dibaca — bukan filter setelah data masuk konteks model.
- **Hanya tiga bentuk keluaran:** jawaban bersitasi, tugas berstatus `PENDING` yang menunggu
  persetujuan manusia, atau penolakan berlasan. Tidak ada jalur keempat.
- **Kontras yang bisa diverifikasi.** Pertanyaan identik *"Tampilkan NIK siswa kelas 7A"*:

  | Peran | Yang dilihat | Audit |
  |-------|--------------|-------|
  | OPERATOR (level 4) | `************0001` | `data_masked: true` |
  | KEPALA MADRASAH (level 5) | `3273051508120001` | `data_masked: false` |

---

## Struktur Repo

```
.
├── expert-package/          # deliverable utama — paket siap pasang di WorkBuddy
│   ├── .codebuddy-plugin/   #   metadata plugin
│   ├── agents/              #   prompt agent (10 layer perilaku)
│   ├── avatars/
│   └── skills/kb-madrasah/  #   skill: 10 dokumen KB + 5 skrip Python + audit log
├── prototype/               # implementasi referensi pipeline 10 layer (Python)
│   ├── asisten_madrasah.py  #   query processor, RBAC, masking, audit
│   ├── test_runner.py       #   48 assertion
│   ├── demo.py              #   demo runner naratif
│   └── make_avatar.py
├── mock-data/               # 10 dokumen sintetis (jadwal, SPP, SOP, RBAC, chat staf, …)
├── live-demo/index.html     # demo interaktif 23 skenario, tanpa dependency
└── docs/                    # arsitektur, accountability sheet, hasil uji, naskah video
```

---

## Cara Pakai

### 1. Pasang Expert Package di WorkBuddy

Salin folder `expert-package/` ke direktori plugin WorkBuddy:

```
~/.workbuddy-ai/plugins/marketplaces/my-experts/plugins/asisten-madrasah/
```

Lalu buka WorkBuddy → **Expert Center → My Experts → Asisten Madrasah**.

> WorkBuddy memuat prompt expert **saat sesi chat dibuka**. Setelah mengubah paket,
> buka sesi baru agar versi terbaru terpakai.

### 2. Jalankan prototipe referensi

```bash
cd prototype
python asisten_madrasah.py          # mode interaktif
python demo.py                      # 11 adegan demo naratif
python test_runner.py               # 48 assertion
```

### 3. Buka demo interaktif

Buka `live-demo/index.html` langsung di browser — tidak perlu server, tidak ada dependency.

---

## RBAC — 7 Peran

| Peran | Level | Cakupan |
|-------|-------|---------|
| ALUMNI | 0 | Informasi publik saja |
| SISWA | 1 | Data miliknya sendiri |
| ORANG TUA | 1 | Data anaknya |
| GURU | 2 | Kelas & mapel yang diampu |
| WALI KELAS | 3 | Satu kelas binaan, termasuk chat wali kelas |
| OPERATOR | 4 | Administrasi penuh, data pribadi ter-mask |
| KEPALA MADRASAH | 5 | Akses penuh, tanpa masking |

---

## 5 Pilar Akuntabilitas

| Pilar | Implementasi | Bukti |
|-------|--------------|-------|
| Menunjukkan sumber | Sitasi dokumen + bagian di setiap jawaban | Trace `Read Jadwal_Pelajaran_Kelas_7_8_9.md` |
| Tahu batas kewenangan | RBAC diperiksa di L4, sebelum retrieval | *"Anda hanya dapat melihat nilai Anda sendiri."* |
| Minta izin sebelum bertindak | Approval gate untuk semua aksi eksternal | 4 tombol: Setujui · Tolak · Ubah · Jawab klarifikasi |
| Mengakui batasnya | "Tidak tahu" + arahan ke pihak berwenang | *"Hubungi Pembina OSIS."* |
| Menyimpan jejak | Audit log 16 field, JSON Lines, bisa diekspor | 7 interaksi · 6 ALLOWED · 1 DENIED · 1 injection |

Kelima pilar ini dipetakan ke **UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi** —
lihat [`docs/ACCOUNTABILITY_SHEET.md`](docs/ACCOUNTABILITY_SHEET.md) §6.

---

## Hasil Pengujian

- **48/48 test case lulus** — 22 Challenge A + 20 Challenge B + 6 masking
  ([`docs/TEST_RESULTS.md`](docs/TEST_RESULTS.md))
- **6 bug** ditemukan lewat pengujian live yang lolos dari test suite — didokumentasikan
  terbuka, bukan disembunyikan ([`docs/LIVE_VALIDATION.md`](docs/LIVE_VALIDATION.md))
- **Baseline terukur:** ~9 menit manual → ~11 detik via agent per pertanyaan khas
  (pengukuran 5 pertanyaan, lihat [`docs/PROJECT_DESCRIPTION.md`](docs/PROJECT_DESCRIPTION.md) §4)

> Catatan jujur: test suite hijau tidak menjamin apa pun. Empat dari enam bug hanya
> ketahuan saat agent diuji langsung di WorkBuddy.

---

## Dokumentasi

| Dokumen | Isi |
|---------|-----|
| [`docs/PROJECT_DESCRIPTION.md`](docs/PROJECT_DESCRIPTION.md) | Overview, insight, solution design, business value |
| [`docs/ACCOUNTABILITY_SHEET.md`](docs/ACCOUNTABILITY_SHEET.md) | Apa yang bisa diakses, apa yang butuh approval, apa yang tidak akan dilakukan |
| [`docs/ARSITEKTUR.md`](docs/ARSITEKTUR.md) | Arsitektur lengkap 10 layer + trust boundary |
| [`docs/SMART_TASK_HANDLER_WORKFLOW.md`](docs/SMART_TASK_HANDLER_WORKFLOW.md) | Alur 6 tahap Challenge B |
| [`docs/TEST_RESULTS.md`](docs/TEST_RESULTS.md) | 48 test case + hasil |
| [`docs/LIVE_VALIDATION.md`](docs/LIVE_VALIDATION.md) | Bukti live per pilar + matriks celah terbuka |
| [`docs/README_PROJECT.md`](docs/README_PROJECT.md) | Dokumen proyek lengkap (fitur, skenario, tech stack) |

---

## Catatan Data

Seluruh data di repo ini **sintetis** — dibuat untuk keperluan demo (MTsN 1 Jakarta,
Tahun Ajaran 2026/2027). Tidak ada data siswa, guru, atau staf madrasah yang nyata.
Tidak ada email, kalender, atau basis data sungguhan yang disentuh.

---

## Lisensi

[MIT](LICENSE)
