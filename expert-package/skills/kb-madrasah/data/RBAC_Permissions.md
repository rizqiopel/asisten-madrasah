---
title: Kebijakan Keamanan dan Hak Akses (RBAC)
document_type: SECURITY_POLICY
category: GOVERNANCE
last_updated: 2026-10-21
author: Sistem Administrasi Madrasah
---

# ROLE-BASED ACCESS CONTROL (RBAC) POLICY
**ASISTEN MADRASAH - MTsN 1 JAKARTA**

Kebijakan ini mengatur apa yang boleh dan tidak boleh dilakukan oleh setiap pengguna dalam ekosistem digital madrasah.

## 1. Role: SISWA
- **Akses Diizinkan**: Jadwal pelajaran sendiri, Nilai sendiri, Info kegiatan/ekstra, SPP sendiri.
- **Akses Dilarang**: Data siswa lain, Data guru, Keuangan madrasah, Dokumen internal, Smart Task Handler.

## 2. Role: ORANG TUA
- **Akses Diizinkan**: Jadwal anak, Nilai anak, Info SPP anak, Info kegiatan sekolah.
- **Akses Dilarang**: Data siswa lain, Data guru (kecuali kontak wali kelas), Keuangan madrasah, Smart Task Handler.

## 3. Role: GURU
- **Akses Diizinkan**: Jadwal mengajar, Nilai kelas yang diampu (Read/Write), Data siswa di kelasnya, Task terkait.
- **Akses Dilarang**: Data siswa kelas lain, Keuangan madrasah, Chat pribadi orang lain.
- **Fitur Khusus**: Smart Task Handler (Allowed).

## 4. Role: WALI KELAS
- **Akses Diizinkan**: Seluruh akses GURU, Data siswa kelas perwalian (semua mapel), Kontak orang tua perwalian.
- **Fitur Khusus**: Smart Task Handler (Allowed).

## 5. Role: KEPALA MADRASAH
- **Akses Diizinkan**: FULL READ/WRITE (Data, Dokumen, Chat, Task).
- **Fitur Khusus**: Smart Task Handler (Allowed), Audit Log, User Management.

## 6. Role: OPERATOR
- **Akses Diizinkan**: Administrasi, Keuangan, Dokumen, Chat, Task.
- **Ketentuan Data Sensitif**: NIK dan No. Telp wajib di-MASKING (hanya 4 digit terakhir yang terlihat).
- **Fitur Khusus**: Smart Task Handler (Allowed), Audit Log.

## 7. Format Masking Data Sensitif (WAJIB PERSIS)

Ketika data sensitif ditampilkan **ter-mask**, gunakan format di bawah ini **apa adanya**.
Jangan memendekkan, Jangan mengganti tanda hubung, dan jangan menambah digit.

| Jenis Data | Contoh Asli | Format Masking Wajib | Keterangan |
|------------|-------------|----------------------|------------|
| NIK (16 digit) | `3273051508120001` | `************0001` | 12 bintang + **4 digit terakhir** |
| No. Telepon (format `XXXX-XXXX-XXXX`) | `0812-3456-7890` | `****-****-7890` | 4 bintang + tanda hubung + 4 bintang + tanda hubung + **4 digit terakhir** |
| No. Telepon (tanpa tanda hubung) | `081234567890` | `*******7890` | 7 bintang + **4 digit terakhir** |
| No. Telepon Orang Tua | `0813-2211-4455` | `****-****-4455` | Format sama |

**Contoh jawaban yang benar (OPERATOR):**
> NIK: `************0001` · Telepon: `****-****-7890` · Telepon Orang Tua: `****-****-4455`

**Contoh jawaban yang SALAH:**
> NIK: `--0001` · Telepon: `--7890` · Telepon: `*******7890` (tanpa tanda hubung, tidak konsisten)

> **Catatan:** nilai yang belum terisi harus ditulis apa adanya sebagai `belum terisi` —
> **jangan** disamarkan dengan bintang, karena itu akan menyamarkan fakta bahwa datanya
> memang belum ada.

---
*Kebijakan ini berlaku mutlak untuk semua interaksi dengan AI Asisten Madrasah.*
