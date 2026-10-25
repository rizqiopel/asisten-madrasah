# Review Video Demo — Asisten Madrasah

**Diperiksa:** 26 Oktober 2026 · **Metode:** ffprobe + sampling frame (tiap 4–20 detik) + scene detection
**File final:** `06-demo/Asisten-Madrasah-Demo-AICanDoIt-2026.mp4`
**Arsip rekaman asli:** `06-demo/raw/KompetisiTncent_raw.mp4`

---

## 1. Spesifikasi Teknis

| Properti | Nilai | Status |
|----------|-------|--------|
| Durasi | **6:00,5** (360,5 detik) | ✅ di dalam target 5–8 menit |
| Resolusi | 1280×720 (16:9) | ⚠️ script minta 1920×1080 |
| Frame rate | 30 fps konstan | ✅ |
| Video codec | H.264 · yuv420p | ✅ kompatibel semua platform |
| Audio codec | AAC · 48 kHz · stereo · 192 kbps | ✅ |
| Ukuran | 67,5 MB | ✅ aman untuk upload |
| Loudness (asli) | **−24,85 LUFS** · true peak −1,12 dB | ⚠️ terlalu pelan |
| Loudness (final) | **−16,13 LUFS** · true peak −1,33 dB | ✅ sudah dinormalisasi |

> **Yang saya lakukan pada file final:** audio dinormalisasi ke −16 LUFS (standar YouTube/presentasi)
> dengan **stream video di-copy, bukan di-re-encode** — kualitas gambar tidak turun sama sekali.
> Rekaman asli tetap utuh di `06-demo/raw/`.

**Catatan editing:** hanya ada **4 hard cut** di seluruh video (detik 5,0 · 20,6 · 297,7 · 299,4).
Artinya ini praktis **satu take screen recording tanpa montage** — bukan struktur hybrid
60% WorkBuddy / 30% live demo seperti rencana di `VIDEO_SCRIPT.md`. Perpindahan antara
WorkBuddy dan browser terjadi karena pindah jendela, bukan karena cut yang direncanakan.

---

## 2. Peta Isi Video (terverifikasi dari frame)

| Waktu | Yang terlihat | Adegan script |
|-------|---------------|---------------|
| 0:00–0:05 | Title card "Asisten Madrasah" (poster + logo) | 1 (pembuka) |
| 0:05–0:20 | Landing page WorkBuddy "WorkBuddy, ideas into reality" | — *dead air* |
| 0:20 | Expert Center → buka sesi chat Asisten Madrasah | 1 |
| ~1:35 | **[WORKBUDDY]** "Monday schedule for class 7A" — trace: `Read SKILL.md` → `Read Jadwal_Pelajaran_Kelas_7_8_9.md` | 2 ✅ |
| ~2:30 | **[WORKBUDDY]** "Berapa nilai ujian matematika ANDI?" — agent memproses (RBAC) | 3 ✅ |
| ~3:25 | **[LIVE DEMO]** skenario "Jadwal ujian (siswa) — tanpa bocor chat" — *"sudah dilaksanakan pada 16 Oktober 2026 pukul 08.00 WIB"* + panel 5 pilar + audit trail | 4 ✅ |
| ~4:18 | **[LIVE DEMO]** skenario "Ketua OSIS tidak ada di data" — *"tidak menemukan informasi"* → arahkan ke Pembina OSIS | 5 ✅ |
| ~4:52 | **[LIVE DEMO]** "Instruksi jahat disisipkan" (role OPERATOR) — badge **BLOCKED · injection=1** | 7 ✅ |
| ~5:08 | **[WORKBUDDY]** Smart Task — trace: `smart_task.py` → *decompose & validation* → *verify weekdays and inspect NOW constant* | 8 ✅ |
| ~5:12 | **[WORKBUDDY]** tabel 3 task (SEDANG / CF-01 / OVERDUE) + "Tiga hal yang menghalangi eksekusi" + konflik Jumat siang → usul 14.00 WIB | 8 ✅ |
| ~5:25 | **[WORKBUDDY]** "Tampilkan NIK siswa kelas 7A" → jawaban berupa **tabel ringkasan audit log**, kolom *Data di-mask = ya* | 6 ⚠️ |
| ~5:50–6:00 | **[LIVE DEMO]** "Ringkasan audit trail" — 7 interaksi · 6 ALLOWED · 1 DENIED · 1 injection · 2 Smart Task · `data_masked=true` · `PENDING` | 9 ✅ |

**Cakupan:** 8 dari 10 adegan terbukti visual. 2 adegan bermasalah (lihat §3).

---

## 3. Temuan — diurutkan berdasarkan dampak

### 🔴 T-1 · Adegan 6 (masking) tidak terbaca sebagai pasangan kontras

Ini adegan bertanda ⭐ di script, dan justru yang paling lemah di video.

Pertanyaan "Tampilkan NIK siswa kelas 7A" dijawab dengan **tabel ringkasan audit log**
("NIK 3 siswa 7A ditampilkan ter-mask", kolom *Data di-mask: ya*) — bukan daftar NIK.
Penonton **tidak pernah melihat** perbandingan yang jadi inti argumen:

```
OPERATOR  →  ************0001
KEPALA    →  3273051508120001
```

Tanpa itu, juri hanya melihat agent merangkum log audit — bukan bukti bahwa data sensitif
benar-benar ter-mask untuk satu role dan terbuka untuk role lain. **Kontrasnya hilang.**

Selain itu jawaban yang tampil memuat kalimat *"Temuan penting — perlu Anda ketahui: entri
sesi ini belum ada di log saat Anda bertanya"* — jujur, tapi membingungkan di tengah demo.

**Perbaikan:** rekam 2 sesi baru (OPERATOR → tampilkan NIK, lalu KEPALA → tampilkan NIK),
potong 15–20 detik tiap sesi, sisipkan di menit 5:25. Tambahkan 10 detik live demo
skenario "Operator lihat NIK (ter-mask)" vs "Kepala lihat NIK (full)" side-by-side.

### 🔴 T-2 · Approval gate 4 tombol tidak muncul

Adegan 8 berhenti di "Tiga hal yang menghalangi eksekusi" (notulen tidak ada di KB, email
Pak Ahmad tidak ada, konflik Jumat siang). Itu **deteksi konflik** — bagus, dan CF-01
terlihat jelas. Tapi **layar konfirmasi dengan 4 tombol (Setujui / Tolak / Ubah / Jawab
Klarifikasi) tidak pernah tampil**, padahal itu bukti pilar ketiga ("minta izin sebelum
bertindak") dan itu inti Challenge B.

**Perbaikan:** rekam satu skenario Smart Task yang **lolos** validasi (tanpa blocker) supaya
layar approval muncul, lalu klik **Setujui**. 20–25 detik cukup.

### 🟡 T-3 · Dead air ±35 detik

- **0:05–0:20** (15 detik) — landing page WorkBuddy kosong sebelum masuk Expert Center.
- **±4:56–5:00** (4 detik) — landing page yang sama muncul lagi saat pindah jendela.
- **±5:00** — frame "WorkBuddy, ideas into reality" berulang 3× dalam sampling.

**Perbaikan:** potong 0:05–0:20, mulai langsung dari Expert Center (title card 5 detik sudah cukup).
Video jadi 5:45 dan ritmenya jauh lebih padat.

### 🟡 T-4 · Resolusi 720p, teks UI kecil

Script merencanakan 1920×1080. Di 720p, teks chat WorkBuddy masih terbaca di layar penuh,
tapi saat video ditonton di panel kecil (mis. preview submission), detail trace tool
(`Read SKILL.md`, `audit_logger.py`) akan hilang. Sayang, karena justru itu bukti kerja agent.

**Perbaikan:** kalau ada waktu, re-record di 1080p dengan zoom UI WorkBuddy 125%.
Kalau tidak, tambahkan **zoom-in cut** 2–3 detik pada bagian kritis (baris NIK, badge
BLOCKED, baris DENIED) saat editing.

### 🟢 T-5 · Bahasa prompt tidak konsisten

Prompt pertama berbahasa Inggris ("Monday schedule for class 7A"), sisanya Indonesia.
VO-nya Indonesia. Kecil, tapi mengurangi kesan rapi.

### 🟢 T-6 · Audio asli terlalu pelan — **sudah diperbaiki**

Rekaman asli −24,85 LUFS (sekitar 9 dB di bawah standar). File final sudah −16,13 LUFS.
Kalau kamu upload dari file lain, pastikan pakai yang sudah dinormalisasi.

---

## 4. Yang sudah kuat (jangan diubah)

- **Durasi 6:00 pas** — masih ada ruang 2 menit untuk menambal T-1 dan T-2 tanpa melewati 8 menit.
- **Trace tool terlihat** (`Read Jadwal_Pelajaran_Kelas_7_8_9.md`, `smart_task.py`,
  `audit_logger.py`) — ini bukti bahwa agent benar-benar membaca knowledge base, bukan mengarang.
  Banyak peserta hackathon tidak punya bukti sekuat ini.
- **Konflik CF-01 tersaji rapi** — "Jumat siang bentrok sholat Jumat, usul 14.00 WIB". Sangat konkret.
- **Live URL terlihat jelas** di address bar (`asisten-madrasah-demo.apps.workbuddy.host/...?sharecode=U52RKMFPEM`)
  pada beberapa frame — bagus untuk juri yang ingin mencoba sendiri.
- **Penutup audit trail** kuat: 7 interaksi, 6 ALLOWED, 1 DENIED, 1 injection, 2 Smart Task.
  Angka-angka ini yang diingat juri.

---

## 5. Rencana perbaikan (estimasi 45–60 menit)

| Prioritas | Aksi | Dampak |
|-----------|------|--------|
| 1 | Rekam ulang Adegan 6 (2 sesi NIK + side-by-side live demo), sisipkan di 5:25 | Menyelamatkan adegan bintang |
| 2 | Rekam 1 Smart Task yang lolos validasi → tampilkan 4 tombol → klik Setujui | Bukti pilar ke-3 + Challenge B |
| 3 | Potong dead air 0:05–0:20 | Ritme |
| 4 | Zoom-in pada NIK, badge BLOCKED, baris DENIED | Keterbacaan di 720p |
| 5 | (Opsional) re-record 1080p | Kualitas visual |

Setelah tambalan: durasi jadi sekitar **6:40–7:00** — masih aman di target.

---

## 6. Checklist konten (`VIDEO_SCRIPT.md` §Checklist)

| Item | Status |
|------|--------|
| Q&A dengan sitasi sumber | ✅ terlihat 1:35 |
| RBAC menolak dengan sopan | ✅ prompt terlihat 2:30 (jawaban penolakan tidak tertangkap frame) |
| Konflik sumber dilaporkan terbuka | ✅ 3:25 + 5:12 (CF-01) |
| Pasangan kontras siswa vs staf | ✅ 3:25 (siswa: kalender saja) |
| "Saya tidak tahu" + arahan ke SME | ✅ 4:18 |
| **Masking pasangan kontras** ⭐ | ⚠️ **tidak terbaca** — lihat T-1 |
| Prompt injection diabaikan & dilaporkan | ✅ 4:52 (`BLOCKED · injection=1`) |
| Smart Task: dekomposisi + konflik | ✅ 5:08–5:12 |
| Smart Task: **approval gate** | ⚠️ **tidak muncul** — lihat T-2 |
| Audit trail dengan DENIED + injection | ✅ 5:50 |
| 6 temuan audit (bug) | ❓ VO — tidak bisa diverifikasi dari frame |
| Live URL ditampilkan | ✅ terlihat di address bar |
| UU PDP No. 27/2022 | ❓ VO — tidak bisa diverifikasi dari frame |
| Baseline 9 menit → 11 detik | ❓ VO — tidak bisa diverifikasi dari frame |

> Tiga item bertanda ❓ hanya bisa dipastikan dengan mendengarkan audio. Kalau VO-nya
> belum menyebut UU PDP dan baseline 9 menit → 11 detik, itu dua poin yang paling
> disayangkan untuk juri Indonesia. Keduanya ada di naskah Adegan 10.
