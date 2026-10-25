# Script Video Demo — Asisten Madrasah (Hybrid)

**Durasi target:** 5–8 menit · **Format:** Hybrid — WorkBuddy Expert Center (live chat) + Live Demo HTML
**Tanggal:** 25 Oktober 2026 · **Hackathon:** AI CAN DO IT — Tencent Cloud Indonesia 2026

---

## Strategi Hybrid

Video ini menggabungkan dua sumber tampilan:

| Kode | Sumber | Tujuan |
|------|--------|--------|
| **[WORKBUDDY]** | Live chat di WorkBuddy Expert Center | Bukti LLM asli menjawab |
| **[LIVE DEMO]** | `06-demo/live-demo/index.html` (23 skenario) | Tunjukkan struktur 10-layer + audit panel |
| **[B-ROLL]** | Screenshot / transisi cepat | Konteks visual saat VO |

**Pembagian:** ~60% WorkBuddy live chat, ~30% live demo HTML, ~10% B-roll.

---

## Persiapan

Sebelum mulai rekam:

1. Buka WorkBuddy → Expert Center → My Experts → **Asisten Madrasah**
2. Buka browser → live demo: `https://asisten-madrasah-demo.apps.workbuddy.host/index.html?sharecode=U52RKMFPEM`
   (atau buka file lokal: `06-demo/live-demo/index.html`)
3. Siapkan folder screenshot: `06-demo/screenshots/` (untuk B-roll cadangan)
4. Tutup aplikasi lain, matikan notifikasi
5. Resolusi rekam: 1920×1080, 30fps
6. **Penting:** Gunakan **sesi chat baru** untuk setiap skenario WorkBuddy — WorkBuddy memuat prompt expert saat sesi dibuka

---

## Adegan 1 — Pembuka (0:00–0:45)

**Visual:** [WORKBUDDY] Expert Center, kartu Asisten Madrasah terlihat. Klik kartu untuk membuka sesi chat baru.

**VO:**

> "Assalamu'alaikum. Saya Rizqi, operator MTsN 1 Jakarta. Ini adalah Asisten Madrasah —
> AI assistant yang saya bangun di atas Tencent Cloud WorkBuddy untuk Challenge A,
> The Workplace Brain, plus bonus Challenge B, Smart Task Handler.
>
> Yang membuat proyek ini berbeda: agent ini **bukan sekadar menjawab pertanyaan**.
> Ia mematuhi tujuh peran dengan hak akses berbeda, menunjukkan sumber setiap jawaban,
> dan menolak bertindak tanpa persetujuan manusia. Saya akan tunjukkan lima pilar
> akuntabilitas itu bekerja — bukan di kode, tapi di LLM asli."

**[B-ROLL]** (5 detik di tengah VO): Buka live demo HTML → tampilkan halaman awal dengan 23 skenario + panel akuntabilitas di kanan.

---

## Adegan 2 — Q&A + Sitasi Sumber (0:45–1:30)

**Visual:** [WORKBUDDY] Sesi chat BARU. Ketik:

```
Saya siswa kelas 7A. Jadwal pelajaran kelas 7A hari Senin?
```

**VO:**

> "Pertanyaan dasar. Agent menjawab dengan jadwal lengkap, dan — ini penting —
> menyebut sumbernya: `Jadwal_Pelajaran_Kelas_7_8_9.md`, bagian kelas 7A, Senin.
> Bukan jawaban karangan. Pilar pertama: menunjukkan sumbernya."

**[LIVE DEMO]** (5 detik transisi): Buka skenario "Q&A: Jadwal Kelas 7A" di live demo → tunjukkan panel kanan: layer pipeline berjalan sampai Layer 6 (Sitasi), sumber tercantum.

**Screenshot referensi:** `01_Q&A_Sitasi_SUmber.PNG`

---

## Adegan 3 — RBAC: Penolakan Sopan (1:30–2:00)

**Visual:** [WORKBUDDY] Masih di sesi yang sama. Ketik:

```
Berapa nilai ujian matematika Andi?
```

**VO:**

> "Siswa ini bukan Andi. Ia minta nilai orang lain. Agent menolak — bukan dengan
> 'Akses ditolak', tapi dengan menyebut aturan: 'Anda hanya dapat melihat nilai
> Anda sendiri.' Dan penolakan terjadi **sebelum** dokumen dibaca. Pilar kedua:
> tetap dalam batas kewenangan."

**[LIVE DEMO]** (3 detik transisi): Klik skenario "RBAC: Nilai Siswa Lain" → tunjukkan Layer 4 berubah merah (DENIED) di panel pipeline.

**Screenshot referensi:** `02_RABC.PNG`

---

## Adegan 4 — Konflik Sumber + Pasangan Kontras (2:00–2:55)

**Visual:** [WORKBUDDY] Buka **sesi chat BARU**, ketik:

```
Saya Wali Kelas 7A. Jam berapa ujian PTS Matematika kelas 7A?
```

> ⚠️ Deklarasi role **wajib**: chat wali kelas hanya untuk GURU/WALI/KEPALA/OPERATOR.
> Tanpa menyebut role, agent akan bertanya dulu — itu perilaku benar, bukan error.

**VO:**

> "Ini skenario konflik. Jadwal pelajaran reguler dimulai 07.30, tapi chat wali kelas
> menegaskan ujian kali ini 08.00. Agent memakai 08.00 — sumber yang lebih baru —
> **tapi tidak menyembunyikan konfliknya**. Ia menyebut kedua sumber berdampingan.
>
> Perhatikan juga: agent bilang ujian **sudah dilaksanakan pada 16 Oktober** — bukan
> menyajikannya sebagai acara yang akan datang. Ia sadar hari ini sudah lewat dari
> tanggal ujiannya. Pilar pertama bekerja dua arah: tidak hanya menunjukkan sumber,
> tapi juga mengakui ketegangan."

**[LIVE DEMO]** (8 detik): Klik skenario **"Jadwal ujian (siswa) — tanpa bocor chat"** →
tunjukkan siswa tetap mendapat jawaban lengkap dari kalender; lalu klik
**"Konflik jam ujian PTS (staf)"** → tunjukkan Layer 7 (Konflik) aktif dengan badge WARN.

> **Ini pasangan kontras kedua proyek ini** — pertanyaan identik, role berbeda:
> siswa mendapat kalender saja, staf mendapat rekonsiliasi konflik. Sama kuatnya
> dengan pasangan kontras masking di Adegan 6.

**Screenshot referensi:** `03_Konflik_Sumber_1.PNG`, `03_Konflik_Sumber_2.PNG`

---

## Adegan 5 — Mengakui Batas (2:55–3:25)

**Visual:** [WORKBUDDY] Ketik:

```
Siapa ketua OSIS tahun ini?
```

**VO:**

> "Agent tidak tahu. Dan ia **tidak mengarang**. Alih-alih menebak, ia mengarahkan
> ke Pembina OSIS — orang yang memang berwenang. Pilar keempat: mengakui batasnya.
>
> Ini lebih sulit dari yang kelihatan — banyak model cenderung halusinasi saat
> ditanya hal yang tidak tahu."

**Screenshot referensi:** `04_saya_tidak_tahu.PNG`

---

## Adegan 6 — Masking: Pasangan Kontras (3:25–4:25) ⭐

**Visual:** [WORKBUDDY] Buka **sesi chat baru**. Ketik:

```
Saya Operator. Tampilkan NIK siswa kelas 7A.
```

Tunggu jawaban. Lalu buka **sesi chat baru lagi**. Ketik:

```
Saya Kepala Madrasah. Tampilkan NIK siswa kelas 7A.
```

**VO:**

> "Ini pilar yang paling menentukan: masking data sensitif. Pertanyaannya **identik** —
> 'Tampilkan NIK siswa kelas 7A'. Tapi role-nya berbeda.
>
> Operator melihat NIK `************0001` — dua belas bintang, empat digit terakhir.
> Telepon juga ter-mask. Kewenangan mengakses tidak sama dengan kewenangan melihat utuh.
>
> Kepala Madrasah melihat NIK `3273051508120001` — penuh, karena RBAC memberi akses
> penuh. Audit mencatat `data_masked: true` untuk Operator, `false` untuk Kepala.
>
> Keduanya tercatat di audit trail. Pertanyaan sama, hasil beda — karena role beda."

**[LIVE DEMO]** (10 detik transisi): Klik skenario "RBAC: NIK — Operator (Mask)" → tunjukkan NIK ter-mask + panel audit dengan `data_masked: true`. Lalu klik "RBAC: NIK — Kepala (Full)" → NIK penuh + `data_masked: false`. **Ini memperkuat pasangan kontras** dengan side-by-side comparison yang rapi.

**Screenshot referensi:** `09_Masking_Operator_1.PNG`, `09_Masking_Operator_2.PNG`, `10_Masking_Kepala_1.PNG`, `10_Masking_Kepala_2.PNG`

---

## Adegan 7 — Prompt Injection (4:25–4:55)

**Visual:** [LIVE DEMO] Klik skenario "Pertahanan Injeksi" di live demo HTML.

**VO:**

> "Instruksi berbahaya disisipkan di dalam pesan yang sah. Agent memproses
> 'kirim pengumuman' tapi **mengabaikan** 'hapus semua data siswa' — dan
> melaporkannya sebagai temuan keamanan. Tugas sah tetap jalan, serangan
> diabaikan dan dicatat.
>
> Di panel kanan, lihat Layer 9 — Injection Defense aktif, dan audit mencatat
> `BLOCKED · injection=1`."

**[B-ROLL]** (opsional 3 detik): Tampilkan `06_Prompt_ijection_1.PNG` sebagai bukti WorkBuddy live.

---

## Adegan 8 — Smart Task Handler (4:55–5:55)

**Visual:** [WORKBUDDY] Buka sesi baru sebagai Kepala Madrasah. Ketik:

```
Tolong kirim notulen rapat ke Pak Ahmad, jadwalkan follow-up Jumat jam 12.00, dan update data siswa baru ya.
```

**VO:**

> "Sekarang Challenge B — Smart Task Handler. Pesan panjang ini didekomposisi
> menjadi tiga task terpisah. Agent mendeteksi konflik: follow-up Jumat jam 12.00
> bentrok dengan sholat Jumat.
>
> Lalu — ini yang penting — agent tidak langsung mengeksekusi. Ia menampilkan
> layar konfirmasi dengan empat tombol: Setujui, Tolak, Ubah, atau Jawab Klarifikasi.
> Tidak ada eksekusi otomatis. Pilar ketiga: minta izin sebelum bertindak."

Tunggu layar konfirmasi muncul, lalu klik **Setujui**.

> "Kepala Madrasah menekan Setujui. Baru kemudian agent menjalankan — dan setiap
> langkah tercatat di audit. Jika ditolak tiga kali, task dieskalasi ke Operator,
> bukan diulang tanpa henti."

**[LIVE DEMO]** (5 detik transisi): Klik skenario "Smart Task: Dekomposisi" → tunjukkan 3 task terurai, Layer 9 (Smart Task Handler) aktif, badge SMART di panel.

**Screenshot referensi:** `05_Kepala_Madrasah_1.PNG`, `05_Kepala_Madrasah_2.PNG`, `05_Kepala_Madrasah_3.PNG`

---

## Adegan 9 — Audit Trail (5:55–6:25)

**Visual:** [LIVE DEMO] Klik skenario "Audit Trail" di live demo HTML.

**VO:**

> "Semua interaksi tercatat: waktu, user, role, intent, hasil cek izin, sumber
> yang dibaca. Ada satu baris DENIED — saat siswa mencoba akses nilai orang lain.
> Ada satu temuan keamanan — percobaan injection. Pilar kelima: mencatat jejak.
>
> Audit log ini bisa diekspor ke JSON untuk audit eksternal."

**[B-ROLL]** (3 detik): Tampilkan `07_Audit_log_1.PNG` sebagai bukti WorkBuddy live — tunjukkan tabel audit yang sama di Expert Center.

**Screenshot referensi:** `07_Audit_log_1.PNG` s.d. `07_Audit_log_4.PNG`

---

## Adegan 10 — Penutup + 6 Temuan Audit (6:25–7:50)

**Visual:** [WORKBUDDY] Kembali ke tampilan WorkBuddy. Lalu [B-ROLL] buka live URL di browser: `https://asisten-madrasah-demo.apps.workbuddy.host/index.html?sharecode=U52RKMFPEM`

**VO:**

> "Satu hal yang ingin saya tunjukkan: proyek ini **jujur tentang celahnya**.
>
> Test suite saya 48/48 lulus. Tapi saat saya menguji langsung di WorkBuddy,
> saya menemukan enam bug yang lolos dari test suite:
> pertama, masking ternyata dead code — `data_masked` tidak pernah benar.
> Kedua, file `Data_Siswa_Internal.md` tidak pernah ada di knowledge base.
> Ketiga, format masking belum eksplisit — agent menulis `--7890` bukan `****-****-7890`.
> Keempat, WorkBuddy tidak punya modul autentikasi — role harus dideklarasikan manual.
>
> Yang kelima paling memalukan: **prototipe saya sendiri bocorkan chat staf ke siswa.**
> Jalur jawabannya membaca berkas chat langsung, melewati filter izin — dan test suite
> saya malah **mengunci kebocoran itu** sebagai perilaku yang diharapkan. Yang menemukan
> justru agent WorkBuddy-nya: saat ditanya sebagai siswa, ia menolak memakai chat staf.
> Agent-nya lebih patuh daripada kode dan tes saya sendiri.
>
> Dan yang keenam: prototipe tidak sadar waktu. Ujian 16 Oktober disajikannya sebagai
> acara yang akan datang, padahal hari itu sudah lewat. Agent live justru bilang
> 'masa PTS sudah selesai'.
>
> Semuanya hanya bisa ditemukan lewat interaksi live — bukan lewat kode.
> Itu sebabnya saya dokumentasikan dua lapis bukti: test suite untuk regresi,
> dan screenshot live untuk perilaku LLM asli. Celah masking sekarang tertutup
> dengan pasangan kontras yang baru saja kita lihat.
>
> Demo ini juga live online — link ada di deskripsi proyek.
>
> Dua hal terakhir. Pertama: lima pilar akuntabilitas ini bukan sewenang —
> mereka dipetakan ke **UU No. 27 Tahun 2022 tentang Pelindungan Data
> Pribadi**. Sitasi sumber = transparansi. RBAC = pembatasan tujuan.
> Audit trail = akuntabilitas pengendali data. Juri Indonesia akan
> menangkap: ini bukan demo main-main.
>
> Kedua: saya ukur sendiri. Lima pertanyaan khas yang saya jawab manual
> setiap hari — rata-rata sembilan menit per pertanyaan. Via agent:
> sebelas detik. Bukan target, bukan klaim — pengukuran kasar yang nyata.
>
> Ini agent yang bisa saya percaya di madrasah saya. Terima kasih."

---

## Tips Rekaman

1. **Gunakan sesi chat baru untuk setiap skenario WorkBuddy** — WorkBuddy memuat prompt expert saat sesi dibuka. Sesi lama masih memakai versi lama paket.
2. **Jeda 2–3 detik setelah mengetik** — beri waktu agent menjawab sebelum bicara.
3. **Zoom in ke bagian penting** — NIK ter-mask, tombol approval, baris audit DENIED.
4. **Kalau agent salah jawab**, jangan cut — tunjukkan recovery. Itu justru menunjukkan ketahanan.
5. **Transisi WorkBuddy → live demo:** bisa pakai split screen atau cut langsung. Yang penting juri lihat bahwa kedua sumber menunjukkan hal yang sama.
6. **Urutan rekaman yang efisien:** Rekam semua adegan WorkBuddy dulu (Adegan 1-6, 8), lalu semua adegan live demo (7, 9, transisi), lalu gabungkan saat editing. Atau rekam linear jika lancar.
7. **Total screenshot yang bisa dijadikan B-roll:** 25 file di `06-demo/screenshots/`.

---

## Checklist Konten yang Harus Muncul

- [x] Q&A dengan sitasi sumber (Adegan 2) — WORKBUDDY + LIVE DEMO
- [x] RBAC menolak dengan sopan (Adegan 3) — WORKBUDDY + LIVE DEMO
- [x] Konflik sumber dilaporkan terbuka (Adegan 4) — WORKBUDDY + LIVE DEMO
- [x] **Pasangan kontras kedua**: siswa (kalender saja) vs staf (rekonsiliasi konflik) — WORKBUDDY + LIVE DEMO
- [x] "Saya tidak tahu" + arahan ke SME (Adegan 5) — WORKBUDDY
- [x] **Masking pasangan kontras** OPERATOR vs KEPALA (Adegan 6) ⭐ — WORKBUDDY + LIVE DEMO
- [x] Prompt injection diabaikan & dilaporkan (Adegan 7) — LIVE DEMO + B-ROLL
- [x] Smart Task: dekomposisi + konflik + approval gate (Adegan 8) — WORKBUDDY + LIVE DEMO
- [x] Audit trail dengan DENIED + injection (Adegan 9) — LIVE DEMO + B-ROLL
- [x] Temuan audit: 6 bug yang lolos dari test suite (Adegan 10) — WORKBUDDY + B-ROLL live URL
- [x] Live URL ditampilkan (Adegan 10) — B-ROLL
- [x] **UU PDP No. 27/2022** — sebut di VO bahwa 5 pilar dipetakan ke pasal UU Pelindungan Data Pribadi
- [x] **Baseline nyata** — sebut "9 menit manual → 11 detik via agent" dari pengukuran 5 pertanyaan khas

---

## Estimasi Durasi

| Adegan | Topik | Sumber | Durasi |
|--------|------|--------|--------|
| 1 | Pembuka | WORKBUDDY + B-ROLL | 0:45 |
| 2 | Q&A + sitasi | WORKBUDDY + LIVE DEMO | 0:45 |
| 3 | RBAC penolakan | WORKBUDDY + LIVE DEMO | 0:30 |
| 4 | Konflik sumber + pasangan kontras | WORKBUDDY + LIVE DEMO | 0:55 |
| 5 | Mengakui batas | WORKBUDDY | 0:30 |
| 6 | **Masking kontras** ⭐ | WORKBUDDY + LIVE DEMO | 1:00 |
| 7 | Prompt injection | LIVE DEMO + B-ROLL | 0:30 |
| 8 | Smart Task Handler | WORKBUDDY + LIVE DEMO | 1:00 |
| 9 | Audit trail | LIVE DEMO + B-ROLL | 0:30 |
| 10 | Penutup + 6 temuan + UU PDP + baseline | WORKBUDDY + B-ROLL | 1:25 |
| **Total** | | | **~7:50** |

Dengan jeda natural, estimasi 7–8 menit — masih di dalam target 5–8 menit.

---

## Urutan Rekam yang Efisien

Supaya tidak bolak-balik antara WorkBuddy dan browser:

**Sesi A — WorkBuddy (rekam sekali jalan):**
- Adegan 1 (pembuka + Expert Center card)
- Adegan 2 (Q&A jadwal)
- Adegan 3 (RBAC nilai)
- Adegan 4 (Konflik ujian — **sesi baru, deklarasikan "Saya Wali Kelas 7A"**)
- Adegan 5 (Tidak tahu OSIS)
- Adegan 6 (Masking Operator + Kepala — 2 sesi baru)
- Adegan 8 (Smart Task Handler)
- Adegan 10 ( VO penutup di depan WorkBuddy)

**Sesi B — Live demo HTML (rekam sekali jalan):**
- Adegan 2 transisi (skenario Q&A + panel pipeline)
- Adegan 3 transisi (skenario RBAC + Layer 4 merah)
- Adegan 4 transisi (**2 skenario**: "Jadwal ujian (siswa)" lalu "Konflik jam ujian PTS (staf)" + Layer 7)
- Adegan 6 transisi (skenario masking Operator + Kepala side-by-side)
- Adegan 7 (skenario injection defense)
- Adegan 8 transisi (skenario Smart Task + dekomposisi)
- Adegan 9 (skenario audit trail)

**Sesi C — B-roll (opsional, cepat):**
- Screenshot `06_Prompt_ijection_1.PNG` (3 detik)
- Screenshot `07_Audit_log_1.PNG` (3 detik)
- Browser buka live URL (5 detik)

Lalu saat editing, interleave Sesi A dan Sesi B sesuai urutan adegan.

> **Catatan penting soal deklarasi role:** WorkBuddy tidak punya modul autentikasi,
> jadi setiap skenario yang menyentuh data terbatas **wajib** menyebut role di awal
> pesan. Kalau tidak, agent akan bertanya dulu — itu perilaku benar (anti-spoofing),
> tapi memotong ritme rekaman. Daftar prompt persis per adegan ada di setiap
> bagian adegan di atas.

---

*Script hybrid ini disusun 25 Oktober 2026. Jika ada perubahan pada Expert Package,
verifikasi ulang bahwa setiap prompt di atas masih menghasilkan jawaban yang sesuai
sebelum merekam.*
