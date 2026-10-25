# Asisten Madrasah

Expert package untuk **Tencent Cloud WorkBuddy AI** — asisten operasional madrasah
yang **akuntabel**: selalu menyebut sumber, patuh pada batas akses, dan tidak pernah
mengeksekusi tindakan tanpa persetujuan manusia.

Dibuat untuk **AI CAN DO IT — Tencent Cloud Hackathon Indonesia 2026**
(Challenge A: The Workplace Brain + bonus Challenge B: Smart Task Handler).

---

## Ringkasan

| Aspek | Detail |
|---|---|
| Tipe expert | `agent` (satu persona, banyak role) |
| Kategori | `09-OperationsHR` |
| Bahasa | Bahasa Indonesia (utama), English (sekunder) |
| Konteks | MTsN 1 Jakarta — Tahun Ajaran 2026/2027 |
| Data | 9 dokumen mock (SPP, jadwal, SOP, kalender, chat, task board, RBAC) |
| Eksekusi | **Mock only** — tidak ada email/kalender/database sungguhan |

---

## 5 Pilar Akuntabilitas

1. **Menunjukkan sumbernya** — setiap jawaban diakhiri sitasi `(Sumber: …)`.
2. **Tetap dalam batas akses** — RBAC 7 role ditegakkan di Layer 2 & 4 sebelum retrieval.
3. **Bertanya sebelum bertindak** — Smart Task Handler punya approval gate eksplisit.
4. **Mengakui batasnya** — data tidak ada → "Maaf, saya tidak menemukan…" + arahan ke ahli.
5. **Menyimpan catatan** — audit log 16 field untuk setiap interaksi.

---

## RBAC 7 Role

| Role | Level | Smart Task Handler |
|---|---|---|
| `ALUMNI` | 0 (akses dicabut) | ❌ |
| `SISWA` | 1 | ❌ |
| `ORANG_TUA` | 1 | ❌ |
| `GURU` | 2 | ✅ |
| `WALI_KELAS` | 3 | ✅ |
| `OPERATOR` | 4 | ✅ |
| `KEPALA_MADRASAH` | 5 | ✅ |

> WorkBuddy tidak punya modul autentikasi bawaan. User menyebutkan peran di awal
> percakapan, dan prompt agent menegakkan batas akses berdasarkan peran tersebut.

---

## Struktur Paket

```text
asisten-madrasah/
├── .codebuddy-plugin/
│   └── plugin.json              # metadata & display expert
├── agents/
│   └── asisten-madrasah.md      # prompt 10 layer (inti perilaku)
├── avatars/
│   └── asisten-madrasah.png     # 512x512
├── skills/
│   └── kb-madrasah/
│       ├── SKILL.md             # protokol menjawab + tooling
│       ├── data/                # 9 dokumen mock MTsN 1 Jakarta
│       └── scripts/             # audit logger, smart task, test runner, demo
└── README.md
```

---

## Arsitektur Prompt 10 Layer

| Layer | Isi |
|---|---|
| L1 | Identitas inti — peran, batasan, sumber kebenaran |
| L2 | Konteks role — RBAC 7 level + aturan pewarisan |
| L3 | Klasifikasi intent — 8 kategori |
| L4 | Cek permission — matriks role × intent |
| L5 | Retrieval & sitasi sumber |
| L6 | Deteksi konflik antar sumber |
| L7 | Pengakuan batas + eskalasi ke ahli |
| L8 | Smart Task Handler — 6 tahap (decompose → approve → mock) |
| L9 | Pertahanan prompt injection |
| L10 | Masking data + format audit log |

---

## Smart Task Handler

Enam tahap dengan **approval gate** di tengah:

```
DECOMPOSE → VALIDATE → CLARIFY → CONFIRMATION SCREEN → APPROVAL GATE → EXECUTE (MOCK) + AUDIT
```

**Kode konflik** yang dideteksi:

| Kode | Kondisi |
|---|---|
| CF-01 | Jumat pukul 11.00–13.30 WIB (sholat Jumat) |
| CF-02 | Hari libur nasional |
| CF-03 | Di luar jam kerja 07.00–16.00 |
| CF-04 | Penanggung jawab bentrok jadwal |
| CF-05 | Masa libur semester |
| CF-06 | Setelah pukul 18.00 |

**State machine approval:**

```
PENDING → EXECUTING → COMPLETED
        → EDITING   → PENDING
        → CANCELLED
        → EXPIRED   (timeout)
        → ESCALATED (3x ditolak → Operator)
```

---

## Cara Menjalankan

Semua perintah dijalankan dari `skills/kb-madrasah/`:

```bash
# 40 test case (Challenge A + B)
python scripts/run_tests.py

# Daftar adegan demo
python scripts/demo.py --list

# Jalankan satu adegan demo
python scripts/demo.py --scene 5

# Tulis audit log
python scripts/audit_logger.py append --json '{"role":"SISWA","intent":"SPP"}'

# Baca audit log (hanya KEPALA_MADRASAH / OPERATOR)
python scripts/audit_logger.py read --role KEPALA_MADRASAH --today
```

---

## Status Pengujian

| Challenge | Test | Status |
|---|---|---|
| A — Workplace Brain | 20 | ✅ 20/20 |
| B — Smart Task Handler | 20 | ✅ 20/20 |
| **Total** | **40** | **✅ 40/40 (100%)** |

---

## Batasan yang Disengaja

- **Mock only** — semua aksi eksternal (email, rapat, pengumuman) disimulasikan.
- **Tidak ada autentikasi** — WorkBuddy tidak menyediakannya; role dinyatakan oleh user
  dan ditegakkan oleh prompt.
- **Data statis** — 9 dokumen mock, bukan koneksi ke sistem madrasah sungguhan.
- **Waktu** — semua timestamp WIB (UTC+7).

---

## Lisensi & Kredit

Dibuat oleh **Rizqi** untuk AI CAN DO IT — Tencent Cloud Hackathon Indonesia 2026.
