# Accountability Sheet
## Project: Asisten Madrasah
## Challenge A — The Workplace Brain

---

## 1. What the Agent Can Access

| Data Source | Access Level | Notes |
|------------|--------------|-------|
| Dokumen Madrasah (SOP, Jadwal, Kalender, SPP) | READ | All authenticated users |
| Chat Grup (Wali Kelas, Guru Mapel) | READ | Filtered by role & relevance |
| Chat Pribadi Kepala Madrasah | READ | Kepala Madrasah & Operator only |
| Task Board | READ/WRITE | Based on role permissions |
| Data Siswa (nilai, jadwal, SPP) | READ | Self only (siswa), or child only (orang tua) |
| Data Pribadi (NIK, no. telp) | MASKED | Only last 4 digits shown unless self-query |
| Data Keuangan Madrasah | READ | Kepala Madrasah & Operator only |
| Voice Note / Chat Panjang (Task Input) | READ | Kepala Madrasah, Operator, Guru only |

---

## 2. What the Agent Executes Autonomously

| Action | Autonomous? | Notes |
|--------|-------------|-------|
| Search & retrieve information | ✅ YES | Within permission boundaries |
| Cite sources | ✅ YES | Every answer includes source attribution |
| Detect conflicts between sources | ✅ YES | Flags discrepancies automatically |
| Mask sensitive data | ✅ YES | NIK, phone numbers auto-masked |
| Log queries & responses | ✅ YES | Automatic audit trail |
| Format & present information | ✅ YES | Structured, readable output |
| Decompose chat/voice note into tasks | ✅ YES | Auto-extract tasks, assignee, deadline |
| Detect schedule conflicts (Jumat siang, etc.) | ✅ YES | Auto-flag & suggest alternatives |

---

## 3. What Requires Human Approval

| Action | Approval Required? | Notes |
|--------|-------------------|-------|
| Send email/message to external party | ✅ YES | Confirmation screen with exact recipient & content |
| Update/modify data | ✅ YES | Preview changes before commit |
| Delete data | ✅ YES | Double confirmation required |
| Export data | ✅ YES | Approval + audit log |
| Change user permissions | ✅ YES | Only Kepala Madrasah can approve |
| Execute instructions from documents | ✅ YES | Agent ignores embedded instructions; notifies user |
| Create task from voice note/chat | ✅ YES | Confirmation screen with task summary |
| Schedule meeting | ✅ YES | Confirm time, attendees, agenda |
| Send reminder to staff | ✅ YES | Confirm recipient & message |

---

## 4. What the Agent Will NEVER Do

| Prohibited Action | Safeguard |
|-------------------|-----------|
| ❌ Reveal data to unauthorized users | RBAC enforced before every query |
| ❌ Guess or hallucinate answers | Returns "I don't know" + directs to SME |
| ❌ Execute embedded instructions (prompt injection) | Detects & ignores; notifies user |
| ❌ Act without approval on external actions | Confirmation gate on all outbound actions |
| ❌ Loop indefinitely on errors | Max 3 retries, then escalate to human |
| ❌ Bypass permission checks | Permission check is mandatory, not optional |
| ❌ Log sensitive data in plain text | Logs contain metadata only, not content |
| ❌ Disclose existence of restricted content | Returns same response as non-existent content |
| ❌ Auto-execute tasks from voice note | Always requires confirmation & approval |
| ❌ Schedule during Friday prayers | Auto-detects & suggests alternative time |

---

## 5. Audit & Transparency

- **All queries logged**: timestamp, user ID, query text, sources accessed, response summary
- **Conflict detection logged**: when sources disagree, both sources + resolution noted
- **Approval actions logged**: who approved what, when
- **Rejection logged**: why a query was rejected (permission, not found, etc.)
- **Logs retained**: Minimum 1 year, accessible to Kepala Madrasah & Operator

---

## 6. Mapping ke UU No. 27 Tahun 2022 (Pelindungan Data Pribadi)

Asisten Madrasah tidak hanya memenuhi syarat hackathon — ia selaras dengan
**UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi (UU PDP)** yang berlaku
di Indonesia. Lima pilar akuntabilitas agent dipetakan ke pasal-pasal UU PDP:

| Pilar Asisten Madrasah | Prinsip UU PDP | Pasal | Implementasi di Agent |
|---|---|---|---|
| 🔍 **Shows its sources** — tiap jawaban mencantumkan sumber | Transparansi pengolahan & hak informasi | **Pasal 4 ayat (1) huruf e** (transparansi), **Pasal 5 ayat (1) huruf a** (hak memperoleh informasi) | Setiap jawaban menyebut nama file + bagian. User bisa melacak asal jawaban tanpa harus mempercayai agent begitu saja. |
| 🔒 **Stays within permissions** — RBAC 7 role membatasi akses | Pembatasan tujuan pengolahan & keamanan data | **Pasal 4 ayat (1) huruf b** (pembatasan tujuan), **Pasal 35** (keamanan), **Pasal 36** (kerahasiaan) | Role ditentukan sebelum retrieval. NIK/telepon orang lain di-mask otomatis. Siswa tidak bisa lihat nilai teman. Tujuan pengolahan terbatas pada intent yang dinyatakan. |
| ✅ **Asks before acting** — semua action butuh approval | Transparansi & hak menolak pengolahan | **Pasal 4 ayat (1) huruf e** (transparansi), **Pasal 5 ayat (1) huruf d** (hak menolak pengolahan) | Smart Task Handler selalu menampilkan layar konfirmasi. Tidak ada eksekusi otomatis. User bisa Tolak, Ubah, atau Setujui sebelum agent bertindak. |
| 🙏 **Admits its limits** — "saya tidak tahu" + arahkan ke SME | Akurasi & kualitas data | **Pasal 4 ayat (1) huruf g** (kualitas data), **Pasal 5 ayat (1) huruf c** (hak melengkapi/meluruskan) | Jika data tidak ada, agent tidak mengarang. Ia mengarahkan ke orang yang berwenang (Pembina OSIS, Bagian Kurikulum). Mencegah halusinasi yang bisa menyesatkan. |
| 📋 **Keeps a record** — audit trail 16 field | Akuntabilitas pengendali data | **Pasal 4 ayat (1) huruf f** (akuntabilitas), **Pasal 37** (dokumentasi pengolahan), **Pasal 38** (kebijakan retensi) | Setiap interaksi tercatat: timestamp, user, role, intent, hasil cek izin, sumber yang dibaca, data_masked. Log dapat diekspor untuk audit eksternal. |

### Catatan tambahan

- **Data pribadi yang diproses**: NIK, nomor telepon, nilai siswa — semua
  tergolong "data pribadi" dalam definisi **Pasal 1 angka 2** UU PDP.
- **Data anak**: Siswa madrasah sebagian masih di bawah umur — pemrosesan
  datanya perlu perhatian khusus sesuai **Pasal 4 ayat (1) huruf c**
  (kepentingan yang sah) dan prinsip perlindungan anak.
- **Pengendali data**: Dalam konteks UU PDP, madrasah adalah pengendali data
  (Pengontrol/Pengelola). Asisten Madrasah bertindak sebagai **prosesor**
  yang menjalankan instruksi pengendali dengan batasan yang ditanam di prompt.
- **Hak subjek data**: Agent mendukung hak akses (siswa lihat nilai sendiri),
  hak koreksi (arahkan ke Operator untuk update), dan batas pengolahan
  (tolak jika di luar kewenangan).

> ⚠️ **Disclaimer**: Mapping ini adalah analisis kesesuaian prinsip,
> bukan pendapat hukum formal. Untuk implementasi produksi, konsultasi
> dengan Penasihat Hukum atau DPO madrasah.

### Referensi pasal

- **Pasal 4**: Prinsip pengolahan data pribadi (7 prinsip: sah, pembatasan
  tujuan, kepentingan yang sah, transparansi, akuntabilitas, kualitas data,
  keamanan)
- **Pasal 5**: Hak subjek data (10 hak: informasi, akses, koreksi, hapus,
  portabilitas, dll.)
- **Pasal 35**: Kewajiban keamanan data pribadi
- **Pasal 36**: Kerahasiaan data pribadi
- **Pasal 37**: Dokumentasi pengolahan data pribadi
- **Pasal 38**: Kebijakan retensi data pribadi

---

## 7. Escalation Paths

| Scenario | Action |
|----------|--------|
| Query outside agent's knowledge | Direct to subject-matter expert (SME) |
| Permission conflict | Escalate to Kepala Madrasah |
| Source conflict unresolved | Flag for human review |
| Potential security issue | Alert Operator + Kepala Madrasah |
| System error | Log + notify technical contact |

---

*This accountability sheet is a living document. Last updated: 25 Oktober 2026 — added UU PDP mapping (Section 6).*
