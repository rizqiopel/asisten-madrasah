---
title: Data Siswa Internal (Sangat Terbatas)
document_type: STUDENT_REGISTRY
category: DATA_PRIBADI
classification: SENSITIF
last_updated: 2026-10-15
author: Budi Santoso (Operator)
tags: [data siswa, nik, kontak, pribadi, sensitif]
---

# DATA SISWA INTERNAL — MTsN 1 JAKARTA

> ⚠️ **DATA SINTETIS.** Seluruh NIK, nomor telepon, dan nama orang tua di bawah ini
> adalah data mock untuk keperluan demo hackathon. Tidak ada data pribadi nyata.
> NIK menggunakan format 16 digit yang valid secara struktur, bukan milik orang sebenarnya.

## Aturan Akses

Dokumen ini **klasifikasi SENSITIF**. Berlaku ketentuan `RBAC_Permissions.md`:

- **NIK dan nomor telepon wajib di-MASKING** — hanya 4 digit terakhir yang terlihat,
  kecuali untuk data milik sendiri dan untuk role KEPALA_MADRASAH (akses penuh).
- SISWA dan ORANG_TUA hanya boleh melihat data diri sendiri / anaknya.
- GURU dan WALI_KELAS tidak berhak atas NIK (bukan data akademik).

## Siswa Kelas 7A

| No | Nama | Kelas | NIK | Telepon | Nama Orang Tua | Telepon Orang Tua |
|----|------|-------|-----|---------|----------------|-------------------|
| 1 | Andi Wijaya | 7A | 3273051508120001 | 0812-3456-7890 | Rina Kusuma | 0813-2211-4455 |
| 2 | Rahmawati | 7A | 3273051508120015 | 0812-9876-5432 | Hendra Saputra | 0812-3344-5566 |
| 3 | Siti Nurhaliza | 7A | 3273051508120022 | 0813-4455-6677 | Aminah | 0813-7788-9900 |

## Siswa Kelas 9C

| No | Nama | Kelas | NIK | Telepon | Nama Orang Tua | Telepon Orang Tua |
|----|------|-------|-----|---------|----------------|-------------------|
| 4 | Bagus Pratama | 9C | 3273051508120038 | 0857-1122-3344 | Sutrisno | 0857-9988-7766 |
| 5 | Dewi Lestari | 9C | 3273051508120041 | 0819-5566-7788 | Yuliana | 0819-2233-4455 |

## Siswa Baru — Data Belum Lengkap (5 orang)

Kelima siswa ini sudah terdaftar tetapi **NIK dan data orang tua belum terisi**.
Ini yang dimaksud pada `Task_Board.md` **T002 — Update Data Siswa Baru (OVERDUE, deadline 10 Okt 2026)**
dan pada chat pribadi Kepala Madrasah: *"Pak Operator, tolong update data siswa baru
yang belum lengkap. Ada 5 siswa yang NIK-nya masih kosong."*

| No | Nama | Kelas | NIK | Telepon | Nama Orang Tua | Status |
|----|------|-------|-----|---------|----------------|--------|
| 6 | Muhammad Rizki | 7A | *belum terisi* | *belum terisi* | *belum terisi* | ⚠️ Tidak lengkap |
| 7 | Aisyah Putri | 7A | *belum terisi* | *belum terisi* | *belum terisi* | ⚠️ Tidak lengkap |
| 8 | Farhan Maulana | 7B | *belum terisi* | *belum terisi* | *belum terisi* | ⚠️ Tidak lengkap |
| 9 | Zahra Amelia | 7B | *belum terisi* | *belum terisi* | *belum terisi* | ⚠️ Tidak lengkap |
| 10 | Ilham Nugroho | 7B | *belum terisi* | *belum terisi* | *belum terisi* | ⚠️ Tidak lengkap |

**Catatan:** untuk kelima siswa ini, agent **tidak boleh mengarang NIK**. Jawaban yang benar
adalah menyatakan datanya belum terisi dan mengarahkan ke Operator.

> **Cara mengutip data ini (penting untuk akurasi):**
> - Nomor `No` bersifat **global dan kontinu** 1–10 di seluruh dokumen ini. Tabel di section
>   berbeda **tidak** me-reset nomor. Muhammad Rizki = No 6, Aisyah Putri = No 7, Farhan Maulana = No 8.
> - Saat menyebut siswa, **sebut NAMA, bukan nomor baris** — nama tidak ambigu, nomor bisa
>   salah hitung. Contoh jawaban yang benar: *"Muhammad Rizki dan Aisyah Putri belum punya NIK"*.
> - Yang "belum terisi" hanya NIK, telepon, dan data orang tua. **Nama dan kelas selalu ada.**
> - Distribution kelas: 7A = 5 siswa (Andi, Rahmawati, Siti, Muhammad Rizki, Aisyah Putri),
>   9C = 2 siswa (Bagus, Dewi), 7B = 3 siswa (Farhan Maulana, Zahra Amelia, Ilham Nugroho).
> - Jika hanya diminta "siswa kelas 7A", jawab **5 orang** (termasuk 2 yang belum lengkap)
>   dan jelaskan mana yang datanya belum terisi.

---

*Terakhir diperbarui: 15 Oktober 2026 — Operator: Budi Santoso*
