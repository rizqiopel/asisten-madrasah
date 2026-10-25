# 🏫 Asisten Madrasah
## AI Assistant untuk Administrasi & Akademik Madrasah

---

## Deskripsi Singkat
AI assistant madrasah yang aman & terpercaya — menjawab pertanyaan siswa, orang tua, dan staff dengan kontrol akses ketat dan audit trail lengkap.

---

## Fitur Utama

### ✅ Informasi Akademik
- Jadwal pelajaran per kelas
- Kalender akademik (ujian, libur, kegiatan)
- Nilai dan raport
- Info ekstrakurikuler

### ✅ Administrasi
- SPP dan iuran
- Prosedur permohonan surat izin
- Kontak staff madrasah
- Pengumuman dan kebijakan

### ✅ Smart Task Handler *(fitur tambahan dari Challenge B)*
- Ubah chat/voice note panjang jadi task terstruktur
- Deteksi ambiguitas (nama orang, waktu, lokasi)
- Validasi jadwal (auto-deteksi konflik Jumat siang)
- Konfirmasi screen sebelum eksekusi
- Approval gate — tidak ada action tanpa persetujuan

### ✅ Keamanan & Akuntabilitas
- **Role-based access control**: 7 role dengan level kepercayaan 0–5
- **Source citation**: Tiap jawaban ada sumbernya
- **Conflict detection**: Deteksi info yang bertentangan (CF-01…CF-06)
- **Audit trail**: Semua query tercatat (16 field, JSON Lines)
- **Data masking**: NIK dan data sensitif di-mask otomatis
- **UU PDP No. 27/2022**: 5 pilar dipetakan ke pasal UU Pelindungan Data Pribadi (lihat `ACCOUNTABILITY_SHEET.md` §6)

---

## 5 Pilar Akuntabilitas

| Pilar | Implementasi |
|-------|-------------|
| 🔍 Shows its sources | Setiap jawaban mencantumkan dokumen/chat/task sumber |
| 🔒 Stays within permissions | RBAC — role menentukan apa yang bisa diakses |
| ✅ Asks before acting | Semua action eksternal butuh persetujuan manusia |
| 🙏 Admits its limits | "Saya tidak tahu" + arahkan ke pihak yang tepat |
| 📋 Keeps a record | Log immutable dari semua query dan respons |

---

## Skenario Penggunaan

### Siswa — Q&A
```
Siswa: "Jadwal pelajaran kelas 7A hari Senin?"
Agent: "Jadwal kelas 7A hari Senin:
• 07:30-09:00: Quran Hadits
• 09:00-10:30: Matematika
• 10:45-12:15: Bahasa Indonesia
(Sumber: Jadwal_Pelajaran_Kelas_7_8_9.md)"
```

### Orang Tua — Q&A
```
Ortu: "Berapa SPP kelas 9?"
Agent: "SPP kelas 9 adalah Rp 450.000/bulan.
(Sumber: SPP_2026_2027.md, Pasal 1)"
```

### Guru — Q&A
```
Guru: "Kapan deadline mengisi nilai PTS?"
Agent: "Deadline mengisi nilai PTS adalah 20 Oktober 2026.
(Sumber: Grup_Guru_Mapel, chat 10 Okt 2026)"
```

### Kepala Madrasah — Smart Task Handler
```
Kepala (Voice Note): "Tolong kirim notulen ke Pak Ahmad, 
jadwalin follow-up Jumat siang, update data siswa baru."

Agent: "📋 3 Task Terdeteksi:
1. Kirim notulen ke Pak Ahmad (Guru Matematika)
2. Jadwalkan follow-up: Jumat, 24 Okt, 14.00 WIB
   ⚠️  Jumat siang = waktu sholat Jumat. Diubah ke 14.00.
3. Update data siswa baru (Operator)

[✅ Approve Semua]  [❌ Tolak]  [✏️ Edit]"
```

### Akses Ditolak
```
Siswa: "Berapa nilai ujian matematika Andi?"
Agent: "Maaf, Anda hanya dapat melihat nilai Anda sendiri."
```

---

## Arsitektur

```
Chat / Expert Center
        │
        ▼
  Layer 1-2   Identitas & Role Context (RBAC 7 level)
        │
        ▼
  Layer 3-4   Intent Classification → Permission Check
        │
        ├── DENY ──────────────────────────► Refusal + Audit
        ▼
  Layer 5-7   Retrieval + Citation + Conflict + Limit
        │
        ├── SMART_TASK (staf) ─────────────► Layer 8: 6 tahap + Approval Gate
        ▼
  Layer 9-10  Injection Defense + Masking + Audit Log
        │
        ▼
     Response (6 template)
```

Lihat `04-arsitektur/ARSITEKTUR.md` untuk detail lengkap, atau
`04-arsitektur/arsitektur-agent.svg` untuk diagram visual.

---

## Tech Stack
- **Platform**: Tencent Cloud WorkBuddy AI
- **Bentuk deliverable**: **Expert Package v2.0** (`plugin.json` + `agents/*.md` + `skills/`)
- **Knowledge & tooling**: Skill `kb-madrasah` — 10 dokumen data + 5 skrip Python
- **RBAC**: ditegakkan di prompt (Layer 2 & 4), bukan modul auth platform
- **Approval & audit**: prompt Layer 8 & 10 + `audit_logger.py` (JSON Lines)
- **LLM**: Tencent Cloud LLM via WorkBuddy

> WorkBuddy AI **tidak** menyediakan Knowledge Base RAG, Authentication/RBAC, atau
> Workflow Builder bawaan. Semua perilaku akuntabilitas diimplementasikan di dalam
> Expert Package — lihat `06-demo/IMPLEMENTASI_WORKBUDDY.md` untuk penjelasan lengkap.

---

## Data Mock
Lihat `MOCK_DATA.md` untuk:
- Dokumen madrasah (SOP, Jadwal, Kalender, SPP)
- Chat export (Grup Wali Kelas, Guru Mapel, Chat Pribadi)
- Task board
- Tabel akses (RBAC)
- 20 test cases

Data ini dibundel ke dalam `skills/kb-madrasah/data/` pada Expert Package.

---

## Dokumen Proyek

### 📦 Paket Submission
| Item | Deskripsi |
|------|-----------|
| `07-submission/SUBMISSION_PACKAGE.md` | **Manifest submit** — daftar file, teks siap paste, pre-flight check |
| `07-submission/upload/` | **11 file siap upload** (67 MB) — dokumen, diagram PNG, cover, video, ZIP kode & screenshot |

### Strategi
| Dokumen | Deskripsi |
|---------|-----------|
| `01-strategi/STRATEGI_HACKATHON.md` | Strategi lengkap untuk hackathon |
| `01-strategi/PROJECT_DESCRIPTION.md` | Deskripsi proyek untuk submission |
| `01-strategi/CHECKLIST.md` | Checklist pre-submission & skrip video |

### Knowledge Base (bundel ke Skill)
| Dokumen | Deskripsi |
|---------|-----------|
| `02-mock-data/MOCK_DATA.md` | Ikhtisar seluruh data mock |
| `02-mock-data/files/` | 10 file data → disalin ke `skills/kb-madrasah/data/` |

### Prompt
| Dokumen | Deskripsi |
|---------|-----------|
| `03-prompts/PROMPT_TEMPLATE.md` | Template prompt 10 layer untuk WorkBuddy |

### Arsitektur
| Dokumen | Deskripsi |
|---------|-----------|
| `04-arsitektur/ARSITEKTUR.md` | Arsitektur, trust boundaries, trade-offs |
| `04-arsitektur/arsitektur-agent.svg` | **Diagram visual arsitektur** |
| `04-arsitektur/ACCOUNTABILITY_SHEET.md` | Lembar akuntabilitas agent |
| `04-arsitektur/SMART_TASK_HANDLER_WORKFLOW.md` | Spesifikasi 6 tahap Smart Task |

### Pengujian
| Dokumen | Deskripsi |
|---------|-----------|
| `05-test-cases/TEST_SMART_TASK_HANDLER.md` | Definisi 20 test Challenge B |
| `05-test-cases/TEST_RESULTS.md` | **Hasil: 48/48 PASSED (100%)** |
| `05-test-cases/LIVE_VALIDATION.md` | **Bukti live per pilar + matriks cakupan & celah** |

### Demo
| Dokumen | Deskripsi |
|---------|-----------|
| `06-demo/Asisten-Madrasah-Demo-AICanDoIt-2026.mp4` | **Demo video 6:00** — 720p30, audio −16 LUFS, 8/10 adegan terverifikasi |
| `06-demo/VIDEO_REVIEW.md` | Review video: peta timestamp, cakupan adegan, temuan & rencana perbaikan |
| `06-demo/VIDEO_SCRIPT.md` | Naskah 10 adegan + VO lengkap |
| `06-demo/live-demo/index.html` | **Demo interaktif** — 23 skenario, 7 role, replay terverifikasi · **[Live URL](https://asisten-madrasah-demo.apps.workbuddy.host/index.html?sharecode=U52RKMFPEM)** |
| `06-demo/PROTOTYPE_DEMO.md` | Cara menjalankan demo & skenario |
| `06-demo/PRODUCT_SHARING.md` | WorkBuddy value + key insights |
| `06-demo/IMPLEMENTASI_WORKBUDDY.md` | Panduan implementasi step-by-step |
| `06-demo/SCREENSHOT_GUIDE.md` | 9 skenario pengambilan screenshot |
| `06-demo/screenshots/` | **25 screenshot** sesi live WorkBuddy |

### Code
| Dokumen | Deskripsi |
|---------|-----------|
| `09-prototype/asisten_madrasah.py` | Implementasi pipeline 10 layer |
| `09-prototype/test_runner.py` | Test suite 48 assertion |
| `09-prototype/demo.py` | Demo runner 11 adegan |
| `09-prototype/make_avatar.py` | Generator avatar 512×512 |
| `08-backup/asisten-madrasah.zip` | **Expert Package siap pasang (60.6 KB)** |
| `AGENT.md` | Technical build guide & konfigurasi agent |

### Expert Package (deliverable utama)
| Komponen | Lokasi |
|----------|--------|
| Metadata expert | `.codebuddy-plugin/plugin.json` |
| Prompt 10 layer | `agents/asisten-madrasah.md` |
| Knowledge + tooling | `skills/kb-madrasah/` (10 data + 5 skrip) |
| Avatar | `avatars/asisten-madrasah.png` |

Terpasang di: `%WORKBUDDY_CONFIG_DIR%/plugins/marketplaces/my-experts/plugins/asisten-madrasah/`

---

## Hasil Pengujian

Diverifikasi otomatis, **48/48 lulus (100%)**:

| Kelompok | Test | Status |
|----------|------|--------|
| A — The Workplace Brain | 22 | 22/22 |
| B — Smart Task Handler | 20 | 20/20 |
| M — Data Masking | 6 | 6/6 |

Cara menjalankan ulang:

```bash
# Dari prototipe
cd 09-prototype && python test_runner.py

# Dari dalam Expert Package
cd skills/kb-madrasah && python scripts/run_tests.py
```

Cakupan: RBAC 7 role, sitasi sumber, resolusi konflik (CF-01…CF-06),
pencegahan prompt injection, **masking data pribadi (M-01…M-06 — memastikan
4 digit terakhir tetap terlihat sesuai RBAC)**, dekomposisi task,
layar konfirmasi, approval gate, mock execution, dan eskalasi setelah
3 kali penolakan.

---

## Temuan dari Audit — 6 bug yang lolos dari test suite

Yang paling menarik dari proyek ini bukan hanya agent-nya bekerja, tapi **pengujiannya
menemukan bug nyata**. Test suite hijau 48/48 ternyata **tidak** menjamin apa pun —
dan keenam temuan berikut hanya bisa ditemukan karena prosesnya jujur.

| # | Temuan | Mengapa lolos dari test suite | Status |
|---|--------|---------------------------------|--------|
| 1 | **Masking adalah dead code** — `data_masked` mustahil `True` pada 42 kombinasi role × query | Test menguji *implementasi referensi*, bukan *kelengkapan knowledge base*. Tidak ada jalur output yang menghasilkan data ter-mask, jadi tidak ada yang mengetes hasilnya | ✅ Ditutup — + jalur akses sah, pola ditulis ulang, Layer 9 diperbaiki, prompt `LAYER 10` ditulis ulang, + 6 test M-01…M-06, dan **bukti live** di `09_Masking_Operator_*.PNG` vs `10_Masking_Kepala_*.PNG` |
| 2 | **`Data_Siswa_Internal.md` tidak pernah ada di knowledge base** — prototipe merujuk file yang tidak dikirim | Test suite tidak memeriksa kelengkapan file knowledge base | ✅ Ditutup — file dibuat (10 siswa sintetis), disalin ke Expert Package, dirujuk eksplisit di `SKILL.md` + prompt |
| 3 | **WorkBuddy tidak punya modul autentikasi** — role harus dideklarasikan user | Deterministik: test suite tidak bisa mensimulasikan user yang belum menyebut role | ✅ Ditutup — protokol deklarasi role di `LAYER 2`: tanya sekali, terapkan, role tidak pernah memberi otorisasi tindakan |
| 4 | **Format masking tidak eksplisit** — agent menampilkan `--7890` (bukan `****-****-7890`) dan salah menghitung nomor baris siswa | Test suite hanya menguji pola masking, bukan format *tampilan* yang dipilih LLM | ✅ Ditutup — `RBAC_Permissions.md` §7 (format wajib) + catatan pengutipan di `Data_Siswa_Internal.md` + prompt diperkuat "salin persis, jangan improvisa" |
| 5 | **Prototipe membocorkan chat staf ke siswa** — jalur jawaban JADWAL membaca `KB["chat_wali"]` **langsung**, melewati filter permission Layer 4/5. Test A-05 bahkan **mengunci kebocoran itu**: dijalankan sebagai SISWA, lalu memastikan `Grup_Wali_Kelas_7A` muncul di jawaban | Test menguji jalur jawaban, bukan jalur izin. Layer 4/5 sudah menyaring `chat_wali` dengan benar — tapi Layer 6 (penjawab) mengambil berkasnya langsung dari KB, bukan dari hasil retrieval | ✅ Ditutup — `RESTRICTED_KEYS` menyaring berkas chat berdasarkan **scope role** (bukan level akses), jalur jawaban bercabang menurut hak baca chat, **+ test A-05b** yang memastikan siswa mendapat jawaban lengkap dari kalender **tanpa satu pun isi chat** |
| 6 | **Prototipe tidak sadar waktu untuk tanggal acara** — ujian 16 Okt disajikan sebagai acara **yang akan datang**, padahal `NOW` mock (21 Okt) dan tanggal nyata (25 Okt) sudah melampauinya | Test A-19 hanya menguji kasus "besok", tidak pernah membandingkan tanggal acara dengan hari ini. Framing temporal bukan bagian dari assertion | ✅ Ditutup — `exam_past = exam_date < today`; jawaban bercabang "**sudah dilaksanakan pada**" vs "**dijadwalkan pada**"; prompt LAYER 5 + bagian *Kesadaran temporal*; **+ test A-05c** (tidak brittle — memeriksa `NOW` saat runtime) |

Temuan 1, 2, 4, dan 5 ditemukan lewat **interaksi live**, bukan lewat kode. Saat agent
menjawab *"tidak ada file `Data_Siswa_Internal.md` — dan saya tidak akan mengarang NIK"*,
itu bukan kegagalan — itu **pilar 4 (mengakui batas) bekerja dengan benar**, sekaligus
membongkar celah yang tidak akan pernah terlihat oleh test suite.

**Temuan 5 yang paling telanjang.** User bertanya sebagai **SISWA**, dan agent WorkBuddy
**dengan benar menolak** memakai chat staf — sementara prototipe justru mengirimkannya.
Dua lapis bukti saling bertentangan, dan yang benar adalah agentnya, bukan tesnya.
Sekarang jadwal ujian ada di `Kalender_Akademik_2026_2027.md` (publik), sehingga siswa
mendapat jawaban lengkap **dan** chat staf tetap terlindungi.

Sekarang kelimanya tertutup, dan masking punya **bukti live berpasangan**:
pertanyaan identik, role berbeda, hasil berbeda — `09_Masking_Operator_*.PNG`
(NIK `************0001`, `data_masked: true`) vs `10_Masking_Kepala_*.PNG`
(NIK penuh, `data_masked: false`).

> Metodologi ini didokumentasikan terbuka di
> [`05-test-cases/LIVE_VALIDATION.md`](05-test-cases/LIVE_VALIDATION.md) —
> termasuk bagian **celah yang masih terbuka**, bukan hanya yang berhasil.

---

## Kompetisi
- **Hackathon**: AI CAN DO IT — Tencent Cloud Hackathon Indonesia 2026
- **Challenge**: A — The Workplace Brain *(dengan fitur tambahan dari Challenge B — Office Agent)*
- **Deadline**: 1 November 2026
- **Demo Day**: 27 November 2026

---

*Dibuat dengan ❤️ oleh Operator Madrasah untuk Operator Madrasah*
