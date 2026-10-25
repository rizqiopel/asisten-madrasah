# Smart Task Handler — Spesifikasi Workflow
## Asisten Madrasah · Challenge B (Bonus) · AI CAN DO IT 2026

---

## 1. Ringkasan

Smart Task Handler adalah fitur bonus yang mengubah **chat panjang / voice note** dari
pimpinan madrasah menjadi **task terstruktur**, mendeteksi konflik jadwal, dan **tidak
pernah mengeksekusi apa pun sebelum manusia menyetujui**.

| Aspek | Nilai |
|-------|-------|
| Role yang boleh | KEPALA_MADRASAH, OPERATOR, GURU, WALI_KELAS |
| Role yang ditolak | SISWA, ORANG_TUA |
| Input | Chat panjang (≥50 karakter) atau voice note Bahasa Indonesia |
| Output | Rencana task + layar konfirmasi |
| Eksekusi | Hanya setelah approval manual |
| Aksi nyata | **Tidak ada** — hanya mock tool |
| Audit | Semua permintaan, hasil dekomposisi, dan status approval dicatat |

### 5 Pilar Akuntabilitas yang Dipenuhi

| Pilar | Implementasi |
|-------|-------------|
| **Source** | Setiap task menunjukkan frasa asli mana di pesan yang menjadi dasarnya |
| **Permission** | Cek role sebelum workflow dimulai; siswa/ortu ditolak sejak awal |
| **Approval** | Approval Gate wajib — state machine menolak eksekusi tanpa `APPROVED` |
| **Limits** | Tanya klarifikasi saat ambigu; berhenti dan escalate setelah 3 kali penolakan |
| **Record** | Audit log lengkap: input → decompose → conflict → approval → eksekusi |

---

## 2. Trigger Conditions

Workflow hanya aktif jika **semua** kondisi terpenuhi:

```yaml
trigger:
  all_of:
    - user_role_in: [KEPALA_MADRASAH, OPERATOR, GURU, WALI_KELAS]
    - intent_classified_as: SMART_TASK
    - message_length: ">= 50 characters  OR  is_voice_note: true"
  any_of:
    - contains_any: [tolong, jadwalin, kirim, ingatkan, update, buat, siapkan,
                     minta, tolongkan, sebarkan, konfirmasi, rapat, email]
    - is_voice_note: true
```

**Jika role ditolak** → balasan tetap dan terukur:

> Maaf, fitur Smart Task Handler hanya tersedia untuk Kepala Madrasah, Operator,
> Wali Kelas, dan Guru. Anda dapat bertanya mengenai jadwal, nilai, SPP, atau
> prosedur administrasi sesuai hak akses Anda.

---

## 3. Enam Tahap Workflow

### Tahap 1 — Decompose
Pecah satu pesan menjadi task terpisah. Setiap task wajib punya:

```json
{
  "task_id": "ST001",
  "action": "send_email | schedule_meeting | create_task | post_announcement | reminder",
  "object": "Notulen rapat PTS",
  "assignee": "Pak Ahmad",
  "target": "Grup Wali Kelas 7A",
  "deadline": "2026-10-20T14:00+07:00",
  "priority": "URGENT | TINGGI | SEDANG | RENDAH",
  "source_span": "kirim notulen rapat ke Pak Ahmad",
  "confidence": 0.92
}
```

**Aturan parsing:**
- Kata kerja pemecah: *kirim, jadwalkan, ingatkan, buat, update, siapkan, minta, sebarkan*.
- Multi-assignee → pisah jadi 2 task (bukan 1 task dengan 2 nama).
- Deadline diekstrak dari konteks ("sebelum 20 Oktober", "hari ini", "besok").
- Priority: `URGENT` jika ada kata *segera, urgent, hari ini, penting*.
- `confidence < 0.6` → anggap ambigu, kirim ke Tahap 3.

### Tahap 2 — Validate (Deteksi Konflik)

| Kode | Kondisi | Peringatan | Usulan |
|------|---------|-----------|--------|
| `CF-01` | Jadwal Jumat pukul 11.00–13.30 WIB | Bentrok sholat Jumat | Geser ke 14.00 WIB |
| `CF-02` | Tanggal termasuk daftar libur nasional | Hari libur nasional | Hari kerja berikutnya |
| `CF-03` | Jadwal di luar jam kerja (07.00–16.00) | Di luar jam kerja | 08.00 WIB hari yang sama |
| `CF-04` | Assignee sudah punya jadwal di waktu itu | Bentrok jadwal assignee | Tawarkan slot kosong |
| `CF-05` | Libur semester / libur sekolah dari Kalender | Kegiatan di masa libur | Hari pertama masuk |
| `CF-06` | Lewat jam 18.00 WIB | Di luar jam operasional | Keesokan harinya |

**Catatan zona waktu** (wajib untuk tim lintas wilayah):
- **WIB** = UTC+7 (Jakarta, sebagian besar madrasah)
- **WITA** = UTC+8 (Bali, Sulawesi, Kalimantan)
- **WIT** = UTC+9 (Papua, Maluku)

Jika pesan menyebut zona waktu tidak jelas → masuk Tahap 3 (Clarify).

### Tahap 3 — Clarify (Hanya Saat Ambigu)

**Bertanya HANYA jika jawabannya tidak jelas. Jangan bertanya untuk hal yang sudah pasta.**

| Kondisi | Pertanyaan |
|---------|-----------|
| Nama ganda | "Ada 2 **Pak Budi**: Pak Budi Santoso (Operator) dan Pak Budi Wijaya (Guru IPA). Maksud Anda yang mana?" |
| Waktu samar | "Anda menyebut *siang*. Mau jam 12.00, 13.00, atau 14.00 WIB?" |
| Tanggal ambigu | "*Besok* berarti 16 Oktober 2026, benar?" |
| Zona waktu hilang | "Untuk rapat ini pakai zona WIB, WITA, atau WIT?" |
| Task tidak lengkap | "Informasi belum lengkap: (1) hari/tanggal, (2) jam, (3) agenda, (4) peserta." |
| Target tidak jelas | "Kirim ke Grup Wali Kelas 7A atau ke seluruh grup wali kelas?" |

**Maksimal 1 putaran pertanyaan.** Jika jawaban masih belum lengkap → lanjut ke
Tahap 4 dengan field yang kosong ditandai `[PERLU KONFIRMASI]`, jangan loop.

### Tahap 4 — Confirmation Screen

Format standar yang wajib ditampilkan:

```text
📋 3 Task Terdeteksi dari pesan Anda:

1. 📧 Kirim notulen rapat
   → Penerima: Pak Ahmad (Wijaya)
   → Subjek: Notulen Rapat PTS
   → Prioritas: Sedang

2. 📅 Jadwalkan follow-up
   → Waktu: Jumat, 24 Oktober 2026 pukul 12.00 WIB
   ⚠️ CF-01: Bertepatan dengan waktu sholat Jumat
   → Usulan: pukul 14.00 WIB

3. 📝 Update data siswa baru
   → Assignee: Operator (Budi Santoso)
   → Deadline: 20 Oktober 2026
   → Prioritas: Tinggi

Ringkasan: 0 diblokir · 1 peringatan konflik · 0 ambigu

[✅ Setujui Semua] [✏️ Ubah] [❌ Tolak]
```

**Wajib memuat:** penerima/tujuan persis, waktu persis, isi persis, seluruh
peringatan konflik, dan ketiga tombol.

### Tahap 5 — Approval Gate

```text
                    ┌──────────┐
        masuk ────▶ │ PENDING  │
                    └────┬─────┘
           ┌─────────────┼──────────────┬─────────────┐
     approve│       reject│        edit │    timeout   │
           ▼             ▼             ▼        5 menit│
     ┌───────────┐  ┌───────────┐  ┌──────────┐   ▼    │
     │ EXECUTING │  │ CANCELLED │  │ EDITING  │ ┌─────────┐
     └─────┬─────┘  └───────────┘  └────┬─────┘ │ EXPIRED │
           │                            │        └─────────┘
     ┌─────┴─────┐                      │
     │           │                save  │
 success      error                     ▼
     ▼           ▼              kembali ke PENDING
┌─────────┐  ┌────────┐
│COMPLETED│  │ FAILED │
└─────────┘  └────────┘
```

**Aturan keras:**
- Tidak ada transisi apa pun ke `EXECUTING` kecuali dari `approve`.
- `timeout: 300 detik` → `EXPIRED`, semua task dibatalkan, user diberi tahu.
- `edit` → kembali ke `PENDING` dengan versi terbaru, approval lama **tidak berlaku**.
- **Escalation:** 3 kali `reject` berturut-turut pada task yang sama → berhenti,
  escalate ke Operator untuk penanganan manual. Tidak boleh loop tanpa batas.

### Tahap 6 — Mock Execution + Audit

```python
def mock_execute(task):
    if task.action == "send_email":
        return f"📧 Mock: Email draft siap dikirim ke {task.assignee} ({task.email})"
    if task.action == "schedule_meeting":
        return f"📅 Mock: Meeting '{task.object}' dijadwalkan {task.deadline}"
    if task.action == "create_task":
        return f"📝 Mock: Task '{task.object}' ditambahkan ke Task Board"
    if task.action == "post_announcement":
        return f"📢 Mock: Pengumuman siap diposting ke {task.target}"
    if task.action == "reminder":
        return f"⏰ Mock: Pengingat disiapkan untuk {task.assignee}"
```

> **Penting:** Tidak ada tool nyata yang terhubung. Kredensial email, token kalender,
> dan akses database tidak pernah ada di dalam agent. Ini adalah batas teknis, bukan
> sekadar kebijakan.

**Bonus (opsional, untuk poin tambahan):**
- **Validator agent**: agent kedua memvalidasi rencana terhadap pesan asli sebelum
  ditampilkan.
- **Konfirmasi ganda** untuk aksi berdampak tinggi: >5 penerima, email eksternal,
  atau yang melibatkan nominal uang.
- **Undo 60 detik** setelah eksekusi mock.

---

## 4. Prompt Layer Siap-Paste (Layer 8 — Smart Task Handler)

```
SMART TASK HANDLER — ATURAN MUTLAK

Jika pesan adalah permintaan panjang berisi lebih dari satu tugas (atau voice note),
Maka:
1. Pecah menjadi daftar task terpisah. Setiap task punya: aksi, objek, penerima,
   waktu, prioritas, dan frasa asal dari pesan.
2. Validasi setiap task terhadap: jam sholat Jumat (11.00-13.30 WIB), daftar libur
   nasional, jam kerja (07.00-16.00 zona waktu pengguna), dan jadwal assignee.
   Jika bentrok → tampilkan peringatan + usulan waktu pengganti.
3. Tanyakan HANYA jika ada ambiguitas nyata (nama ganda, waktu samar, target tidak
   jelas, zona waktu tidak disebut). Jangan tanyakan hal yang sudah jelas.
4. Tampilkan layar konfirmasi berisi penerima, waktu, dan isi persis dari setiap task.
5. JANGAN PERNAH mengeksekusi apa pun sebelum pengguna menekan tombol Setujui.
   Tidak ada kecuali. Tidak ada "otomatis karena mendesak".
6. Semua tool bersifat mock. Jangan pernah mengklaim email benar-benar terkirim.
7. Setelah 3 kali penolakan berturut-turut, berhenti dan eskalasikan ke Operator.
8. Catat ke audit log: input asli, hasil dekomposisi, konflik terdeteksi,
   keputusan pengguna, dan hasil eksekusi.
```

---

## 5. Pemetaan ke Test Cases

| Tahap | Test Cases |
|-------|-----------|
| Decompose | ST-01, ST-13, ST-18 |
| Validate | ST-03, ST-04 |
| Clarify | ST-02, ST-19 |
| Confirmation | ST-05, ST-17 |
| Approval Gate | ST-06, ST-07, ST-20 |
| Permission | ST-08, ST-09 |
| Security | ST-10 |
| Extract | ST-11, ST-12 |
| Execution | ST-14, ST-15 |
| Audit | ST-16 |

---

## 6. Checklist Implementasi

- [ ] Trigger: cek role + intent + panjang pesan
- [ ] Decompose: ekstrak aksi, objek, penerima, deadline, prioritas, source span
- [ ] Validate: 6 aturan konflik (CF-01 s.d. CF-06) aktif
- [ ] Clarify: 6 pola pertanyaan, maksimal 1 putaran
- [ ] Confirmation screen: 3 tombol + semua peringatan
- [ ] Approval Gate: state machine 7 status, timeout 300 detik
- [ ] Escalation: berhenti setelah 3 kali reject
- [ ] Mock tool: 5 aksi, tidak ada tool nyata
- [ ] Audit log: 6 field wajib
- [ ] Test ST-01 s.d. ST-20 lulus (20/20)

---

*Smart Task Handler Workflow — Asisten Madrasah*
*Terakhir diperbarui: 21 Oktober 2026*
