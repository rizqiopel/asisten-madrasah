---
name: kb-madrasah
description: |
  Knowledge base MTsN 1 Jakarta Tahun Ajaran 2026/2027 (10 dokumen mock) +
  tooling audit log & Smart Task Handler. Dipakai oleh expert asisten-madrasah
  untuk menjawab pertanyaan siswa/orang tua/staff madrasah dengan sitasi sumber,
  RBAC 7 role, dan approval gate.
description_en: |
  MTsN 1 Jakarta knowledge base (AY 2026/2027, 10 mock documents) plus audit-log
  and Smart Task Handler tooling for the asisten-madrasah expert.
---

# KB Madrasah — Knowledge Base & Tooling

Sumber data tunggal untuk expert **asisten-madrasah**. Semua jawaban WAJIB berasal dari
file di `data/` — bukan dari pengetahuan umum.

## 1. Data (10 dokumen)

| File | Isi | Kode akses |
|---|---|---|
| `SPP_2026_2027.md` | Rincian SPP per kelas + keringanan | SISWA(self), ORANG_TUA(anak), WALI_KELAS, KEPALA, OPERATOR |
| `Jadwal_Pelajaran_Kelas_7_8_9.md` | Jadwal pelajaran kelas 7/8/9 | SISWA(kelasnya), ORANG_TUA(anak), GURU(mapelnya), WALI_KELAS, KEPALA, OPERATOR |
| `SOP_Permohonan_Surat_Izin.md` | SOP 6 langkah surat izin | Publik — semua role |
| `Kalender_Akademik_2026_2027.md` | Kalender akademik & hari libur | Publik — semua role |
| `Grup_Wali_Kelas_7A.txt` | Arsip chat grup wali kelas 7A | GURU, WALI_KELAS, KEPALA, OPERATOR |
| `Grup_Guru_Mapel.txt` | Arsip chat grup guru mata pelajaran | GURU, WALI_KELAS, KEPALA, OPERATOR |
| `Chat_Pribadi_Kepala_Madrasah.txt` | Chat pribadi kepala madrasah | **KEPALA & OPERATOR only** |
| `Task_Board.md` | 5 task berjalan (T001–T005) | GURU(task terkait), WALI_KELAS, KEPALA, OPERATOR |
| `RBAC_Permissions.md` | Matriks akses lengkap | Sistem internal — **jangan** tampilkan ke user |
| `Data_Siswa_Internal.md` | Daftar siswa + NIK & telepon (data sintetis) | OPERATOR (ter-mask), KEPALA (penuh); SISWA/ORTU hanya data sendiri |

**DILARANG** untuk SISWA/ORANG_TUA: `Task_Board.md`, `Grup_*.txt`,
`Chat_Pribadi_Kepala_Madrasah.txt`, `RBAC_Permissions.md`, `Data_Siswa_Internal.md`.

**Masking wajib:** setiap NIK/telepon yang keluar untuk data orang lain harus ter-mask —
hanya 4 digit terakhir terlihat (`************0001`, `****-****-7890`). Pengecualian hanya
untuk data milik sendiri dan role KEPALA_MADRASAH. Lima siswa baru di
`Data_Siswa_Internal.md` belum punya NIK — **jangan dikarang**.

### Petunjuk retrieval — jam & jadwal ujian

Jadwal ujian terperinci (tanggal, jam, ruang) ada di **`Kalender_Akademik_2026_2027.md`**
seksi *Jadwal Ujian PTS* — **bersifat publik, semua role boleh menjawabnya**.
Berkas `Grup_Wali_Kelas_7A.txt` juga memuat informasi yang sama, tetapi
**hanya untuk GURU, WALI_KELAS, KEPALA_MADRASAH, OPERATOR**.

Untuk pertanyaan "jam berapa ujian X?":
1. Selalu mulai dari `Kalender_Akademik_2026_2027.md` (aman untuk semua role).
2. Jika role user boleh membaca chat wali kelas, tambahkan rujukan chat sebagai
   **konfirmasi/pembaruan** — bukan sebagai satu-satunya sumber.
3. Jika role user **tidak** boleh membaca chat (SISWA, ORANG_TUA, ALUMNI), jawab
   dari kalender saja. **Jangan pernah** menyebut isi, pengirim, atau tanggal chat.
   Kalau ada perubahan jadwal yang hanya ada di chat, arahkan user ke Wali Kelas.

## 2. Protokol Menjawab

1. Tentukan **role** user (Layer 2 prompt agent). Belum jelas → tanya dulu.
2. Klasifikasikan **intent**: JADWAL / NILAI / SPP / SOP / TASK / KONTAK / SMART_TASK / GENERAL.
3. Cek **permission** (Layer 4). DENY → hentikan, jangan bocorkan sebagian.
4. Baca file yang relevan dari `data/`.
5. Jawab + **selalu** kutip: `(Sumber: <nama_file>, <bagian>)`.
6. Konflik antar sumber → tampilkan keduanya + alasan pemilihan.
7. Tidak ada di data → "Maaf, saya tidak menemukan informasi tentang [X]…" + arahkan ke ahli terkait.

## 3. Tooling

### `scripts/audit_logger.py`
```bash
# Tambah satu entri log (JSON Lines)
python scripts/audit_logger.py append --json '{"role":"SISWA","intent":"SPP",...}'

# Baca log (hanya KEPALA_MADRASAH / OPERATOR)
python scripts/audit_logger.py read --role KEPALA_MADRASAH --today
python scripts/audit_logger.py read --role OPERATOR --all
```
Log tersimpan di `logs/audit.jsonl` (relatif ke folder skill).
Field wajib: lihat Layer 10 prompt agent (16 field).

### `scripts/smart_task.py`
```bash
# Pecah pesan menjadi tugas
python scripts/smart_task.py decompose --input "Kirim notulen ke Pak Ahmad, jadwalkan rapat Jumat siang"

# Validasi konflik CF-01..CF-06
python scripts/smart_task.py validate --file tasks.json

# Simulasi approval state machine
python scripts/smart_task.py approve --file tasks.json --decision approve
```

### `scripts/run_tests.py`
```bash
python scripts/run_tests.py           # jalankan 48 test case (Challenge A + B + masking)
```
Target: **48/48 lulus**. Output tabel markdown siap ditempel ke laporan.

### `scripts/demo.py`
```bash
python scripts/demo.py --list         # daftar 11 adegan demo
python scripts/demo.py --scene 5      # jalankan satu adegan (adegan sebelumnya ikut senyap)
```

### `scripts/asisten_madrasah.py`
Referensi implementasi lengkap 10 layer (dipakai oleh `run_tests.py` dan `demo.py`).
Baca file ini jika butuh detail perilaku persis (pola regex, aturan konflik, dsb).

## 4. Batasan

- **Mock only** — tidak ada email, kalender, atau database sungguhan.
- Semua waktu memakai **WIB (UTC+7)**.
- Tahun ajaran aktif: **2026/2027**.
- Jangan pernah menampilkan isi file mentah ke user — selalu ringkas + sitasi.
