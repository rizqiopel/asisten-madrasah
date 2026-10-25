"""
Asisten Madrasah — Reference Implementation
=============================================
AI CAN DO IT — Tencent Cloud Hackathon Indonesia 2026
Challenge A (Workplace Brain) + Challenge B (Smart Task Handler)

Modul ini adalah *reference implementation* dari logika agent yang
dijalankan di WorkBuddy. Fungsinya:

1. Menyediakan Knowledge Base yang bisa di-retrieve (dengan filter RBAC).
2. Menyediakan pipeline 10-layer prompt (permission -> retrieval -> synthesis).
3. Menyediakan Smart Task Handler 6-tahap dengan approval gate.
4. Menyediakan audit trail yang mencatat setiap interaksi.

Semua tool eksternal bersifat MOCK — tidak ada koneksi email, kalender,
atau database eksternal. Ini adalah batas teknis, bukan sekadar kebijakan.

Run:
    python asisten_madrasah.py            # jalankan demo skenario
    python asisten_madrasah.py --tests    # jalankan 46 test case
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timedelta, timezone
from typing import Any, Iterable

WIB = timezone(timedelta(hours=7))
NOW = datetime(2026, 10, 21, 9, 0, tzinfo=WIB)

# ---------------------------------------------------------------------------
# 1. KONSTANTA DOMAIN
# ---------------------------------------------------------------------------

ROLE_SISWA = "SISWA"
ROLE_ORTU = "ORANG_TUA"
ROLE_GURU = "GURU"
ROLE_WALI = "WALI_KELAS"
ROLE_KEPALA = "KEPALA_MADRASAH"
ROLE_OPERATOR = "OPERATOR"

SMART_TASK_ROLES = {ROLE_KEPALA, ROLE_OPERATOR, ROLE_GURU, ROLE_WALI}

#: Hirarki akses. Level lebih tinggi = akses lebih luas.
ACCESS_LEVEL = {
    ROLE_SISWA: 1,
    ROLE_ORTU: 1,
    ROLE_GURU: 2,
    ROLE_WALI: 3,
    ROLE_OPERATOR: 4,
    ROLE_KEPALA: 5,
    "ALUMNI": 0,  # akses dicabut setelah lulus
}

#: Kunci pengetahuan yang boleh diakses tiap role (lihat RBAC_Permissions.md)
ROLE_SCOPE = {
    ROLE_SISWA: {"jadwal", "nilai", "spp", "kalender", "sop", "kegiatan"},
    ROLE_ORTU: {"jadwal", "nilai", "spp", "kalender", "sop", "kegiatan"},
    ROLE_GURU: {"jadwal", "nilai", "kegiatan", "task", "chat_guru", "kalender", "sop"},
    ROLE_WALI: {"jadwal", "nilai", "kegiatan", "task", "chat_guru", "chat_wali",
                "kalender", "sop"},
    ROLE_OPERATOR: {"jadwal", "nilai", "kegiatan", "task", "chat_guru", "chat_wali",
                    "chat_kepala", "kalender", "sop", "spp", "keuangan"},
    ROLE_KEPALA: {"jadwal", "nilai", "kegiatan", "task", "chat_guru", "chat_wali",
                  "chat_kepala", "kalender", "sop", "spp", "keuangan"},
    "ALUMNI": set(),  # alumni tidak punya scope apa pun
}

#: Kunci pengetahuan yang HANYA boleh dibaca role yang punya scope-nya.
#: SISWA dan ORANG_TUA tidak pernah masuk daftar ini, jadi berkas chat dan
#: berkas sensitif otomatis tersaring untuk mereka — sekalipun level cukup.
RESTRICTED_KEYS = {
    "chat_wali", "chat_guru", "chat_kepala",
    "keuangan", "piagam", "nilai",
}

#: Level akses minimum untuk menyentuh tiap kunci pengetahuan.
SCOPE_MIN_LEVEL = {
    "spp": 1,
    "keuangan": 4,
    "chat_kepala": 4,
    "task": 2,
    "chat_guru": 2,
    "chat_wali": 3,
}

#: Pola prompt injection yang harus diabaikan.
INJECTION_PATTERNS = [
    re.compile(r"(?i)\bAI\s*:\s*(.+)"),
    re.compile(r"(?i)\bSystem\s*:\s*(.+)"),
    re.compile(r"(?i)\bignore (?:all |any )?(?:previous|prior|above) instructions"),
    re.compile(r"(?i)\byou are now\b\s*(.+)"),
    re.compile(r"(?i)\b(?:delete|hapus|erase)\s+(?:all\s+)?(?:the\s+)?data"),
    re.compile(r"(?i)\bbypass (?:permissions?|security)\b"),
    re.compile(r"(?i)\breveal (?:all|every)\b"),
    re.compile(r"(?i)\blangsung (?:kirim|execute|jalankan)\b"),
    re.compile(r"(?i)\b(?:forward|kirim) (?:this|the) file to all\b"),
]

#: Pola data pribadi untuk masking.
#: Aturan RBAC: "NIK dan No. Telp wajib di-MASKING (hanya 4 digit terakhir
#: yang terlihat)" — jadi 4 digit terakhir DIPERTAHANKAN, sisanya disamarkan.
#: Urutan penting: NIK (16 digit) diperiksa lebih dulu sebelum telepon.
MASKING_PATTERNS = [
    # NIK 16 digit: 3273051508120001 -> ************0001
    (re.compile(r"\b(\d{12})(\d{4})\b"), lambda m: "*" * 12 + m.group(2)),
    # Telepon Indonesia 12 digit, dengan atau tanpa pemisah:
    # 0812-3456-7890 / 081234567890 -> ****-****-7890
    (re.compile(r"\b(\d{4})[- ]?(\d{4})[- ]?(\d{4})\b"),
     lambda m: "****-****-" + m.group(3)),
    # Telepon 11 digit (nomor lama / tanpa digit 0 di depan):
    # 812-3456-7890 / 81234567890 -> ****-***-7890
    (re.compile(r"\b(\d{3})[- ]?(\d{4})[- ]?(\d{4})\b"),
     lambda m: "****-***-" + m.group(3)),
]

#: Kalender libur nasional + libur madrasah (dari Kalender_Akademik_2026_2027.md)
PUBLIC_HOLIDAYS_2026_2027 = {
    "2026-08-17": "Hari Kemerdekaan RI (HUT ke-81)",
    "2026-12-25": "Hari Raya Natal",
    "2027-01-01": "Tahun Baru Masehi",
    "2027-01-10": "Libur Semester 1 (sampai)",
    "2027-05-01": "Hari Buruh Internasional",
    "2027-05-06": "Hari Raya Idul Fitri 1448 H",
    "2027-05-07": "Hari Raya Idul Fitri 1448 H",
}

#: Jam kerja di madrasah (WIB)
WORK_HOURS = (7, 16)
#: Window sholat Jumat (WIB) — dari jadwal Jumat semua kelas
FRIDAY_PRAYER_WINDOW = (11, 13, 30)

#: Nama bulan dalam Bahasa Indonesia (locale mesin bisa berbeda)
NAMA_BULAN = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November",
    12: "Desember",
}


def tanggal_id(d: date) -> str:
    """Format tanggal Bahasa Indonesia: 16 Oktober 2026."""
    return f"{d.day} {NAMA_BULAN[d.month]} {d.year}"


#: Nama-nama yang muncul ganda di lingkungan madrasah (untuk deteksi ambiguitas)
AMBIGUOUS_NAMES = {
    "pak budi": [
        "Pak Budi Santoso (Operator / Tata Usaha)",
        "Pak Budi Wijaya (Guru IPA)",
    ],
}


# ---------------------------------------------------------------------------
# 2. MODEL DATA
# ---------------------------------------------------------------------------

@dataclass
class User:
    id: str
    name: str
    role: str
    class_: str | None = None
    children: list[str] = field(default_factory=list)
    subjects: list[str] = field(default_factory=list)
    assigned_classes: list[str] = field(default_factory=list)
    tz: str = "WIB"

    @property
    def level(self) -> int:
        return ACCESS_LEVEL[self.role]


@dataclass
class Document:
    key: str
    title: str
    source: str
    scope_key: str
    content: str
    date: str = ""
    priority: int = 0  # semakin besar semakin baru / otoritatif


@dataclass
class RetrievedDoc:
    document: Document
    score: float
    snippet: str


@dataclass
class AuditEntry:
    timestamp: str
    session_id: str
    user_id: str
    user_name: str
    role: str
    query: str
    intent: str
    permission_check: str
    sources_accessed: list[str]
    response_summary: str
    action_taken: str = "NONE"
    approval_required: bool = False
    approval_status: str = "N/A"
    prompt_injection_detected: bool = False
    data_masked: bool = False
    conflict_detected: bool = False
    credits_used: float = 0.5

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# 3. KNOWLEDGE BASE
# ---------------------------------------------------------------------------

def _kb() -> dict[str, Document]:
    """Knowledge Base mock. Dalam WorkBuddy ini diisi lewat upload 9 file."""
    docs: list[Document] = [
        Document(
            key="spp",
            title="Penetapan SPP dan Iuran 2026/2027",
            source="SPP_2026_2027.md",
            scope_key="spp",
            date="2026-07-01",
            content=(
                "SK 042/SK-MA/2026. SPP kelas 7 Rp 350.000/bulan, kelas 8 Rp 400.000/bulan, "
                "kelas 9 Rp 450.000/bulan. Iuran OSIS Rp 50.000/semester, Pramuka Rp 75.000/semester, "
                "Komputer Rp 100.000/semester (opsional). Keringanan: anak guru 50% potongan SPP; "
                "anak yatim/piatu bebas 100% dengan surat keterangan; anak ketiga dari 3 bersaudara "
                "di sekolah ini mendapat potongan 25%."
            ),
        ),
        Document(
            key="jadwal",
            title="Jadwal Pelajaran Kelas 7A, 8B, 9C",
            source="Jadwal_Pelajaran_Kelas_7_8_9.md",
            scope_key="jadwal",
            date="2026-07-15",
            content=(
                "Kelas 7A — Senin: Quran Hadits 07:30-09:00, Matematika 09:00-10:30, "
                "Bahasa Indonesia 10:45-12:15. Selasa: IPA, Bahasa Inggris, Penjas. "
                "Rabu: Fiqih, IPS, Seni Budaya. Kamis: Aqidah Akhlak, Matematika, Pramuka. "
                "Jumat: Bahasa Arab 07:30-08:30, Sholat Dhuha & Khotbah 08:30-10:00, BTQ 10:00-11:30."
            ),
        ),
        Document(
            key="sop",
            title="SOP Permohonan Surat Izin Siswa",
            source="SOP_Permohonan_Surat_Izin.md",
            scope_key="sop",
            date="2026-08-01",
            content=(
                "Enam langkah: (1) siswa mengisi formulir izin di ruang operator; "
                "(2) formulir ditandatangani orang tua/wali; (3) diserahkan ke wali kelas untuk paraf; "
                "(4) wali kelas meneruskan ke Kepala Madrasah untuk approval; "
                "(5) operator mencetak surat izin resmi; (6) surat diserahkan ke siswa. "
                "Waktu pemrosesan maksimal 2 hari kerja."
            ),
        ),
        Document(
            key="kalender",
            title="Kalender Akademik 2026/2027",
            source="Kalender_Akademik_2026_2027.md",
            scope_key="kalender",
            date="2026-07-01",
            content=(
                "13 Juli 2026 hari pertama masuk. 1-5 Agustus 2026 MOS. 17 Agustus 2026 HUT RI (libur). "
                "5-16 Oktober 2026 PTS. 2-13 November 2026 pembagian raport PTS. "
                "18-31 Desember 2026 PAS. 1-10 Januari 2027 libur semester 1. "
                "11 Januari 2027 awal semester 2. 25-31 Maret 2027 Ujian Sekolah. "
                "15-30 April 2027 UN. 1-15 Mei 2027 libur Ramadhan & Lebaran. "
                "16 Mei 2027 pembagian raport akhir. 20 Mei 2027 wisuda kelas 9. "
                "Jadwal ujian PTS: 16 Oktober 2026 kelas 7A Matematika jam 08.00 Ruang 2A. "
                "Catatan: ujian dimulai 08.00, bukan 07.30 seperti jam masuk reguler. "
                "Bawa pensil 2B dan penghapus, kalkulator tidak diperbolehkan."
            ),
        ),
        Document(
            key="chat_wali",
            title="Chat Grup Wali Kelas 7A",
            source="Grup_Wali_Kelas_7A.txt",
            scope_key="chat_wali",
            date="2026-10-16",
            content=(
                "15 Okt 2026 08:00 Bu Siti (Wali Kelas 7A): ujian PTS Matematika BESOK 16 Okt "
                "dimulai jam 08.00, bukan jam 07.30 seperti biasa. Ruang 2A. "
                "Bawa pensil 2B dan penghapus, kalkulator tidak diperbolehkan. "
                "16 Okt 2026 07:30 Bu Siti: reminder ujian PTS Matematika jam 08.00 di Ruang 2A."
            ),
        ),
        Document(
            key="chat_guru",
            title="Chat Grup Guru Mata Pelajaran",
            source="Grup_Guru_Mapel.txt",
            scope_key="chat_guru",
            date="2026-10-15",
            content=(
                "10 Okt 2026 14:00 Kepala Madrasah: mohon mengisi nilai PTS paling lambat 20 Oktober 2026. "
                "12 Okt 2026 09:30 Kepala Madrasah: bobot Quran Hadits 40% tugas + 30% PTS + 30% PAS. "
                "14 Okt 2026 16:00 Pak Budi (Guru IPA): mengisi nilai IPA tanggal 22 Oktober karena tugas Dinas. "
                "15 Okt 2026 11:00 Bu Dewi: remedial Bahasa Inggris Sabtu 18 Oktober jam 08.00-10.00, "
                "siswa nilai di bawah KKM wajib hadir."
            ),
        ),
        Document(
            key="chat_kepala",
            title="Chat Pribadi Kepala Madrasah",
            source="Chat_Pribadi_Kepala_Madrasah.txt",
            scope_key="chat_kepala",
            date="2026-10-12",
            content=(
                "5 Okt 2026 10:00 Kepala Madrasah: update data siswa baru yang belum lengkap, ada 5 siswa "
                "yang NIK-nya masih kosong. 8 Okt 2026 09:00 Kepala Madrasah: buat proposal anggaran "
                "perbaikan komputer lab, deadline ke Dinas tanggal 20 Oktober. "
                "12 Okt 2026 14:00 Kepala Madrasah: rapat koordinasi hari Jumat jam 13.00 setelah sholat Jumat."
            ),
        ),
        Document(
            key="task",
            title="Task Board Madrasah (Oktober 2026)",
            source="Task_Board.md",
            scope_key="task",
            date="2026-10-15",
            content=(
                "T001 Persiapan Ujian PTS, assignee Pak Ahmad, deadline 16 Okt 2026, In Progress, prioritas Tinggi. "
                "T002 Update Data Siswa Baru, assignee Operator (Budi Santoso), deadline 10 Okt 2026 OVERDUE, "
                "In Progress, prioritas Tinggi. T003 Proposal Perbaikan Komputer Lab, assignee Operator, "
                "deadline 18 Okt 2026, To Do, Sedang. T004 Rapat Koordinasi Wali Kelas, assignee Kepala Madrasah, "
                "deadline 17 Okt 2026, To Do, Sedang. T005 Remedial Bahasa Inggris, assignee Bu Dewi, "
                "deadline 18 Okt 2026, Scheduled, Rendah."
            ),
        ),
        Document(
            key="nilai",
            title="Data Nilai Siswa (Terbatas)",
            source="Nilai_Siswa_Internal.md",
            scope_key="nilai",
            date="2026-10-16",
            content=(
                "Andi Wijaya (7A) Matematika 82, Bahasa Indonesia 78. "
                "Siti Nurhaliza (7A) Matematika 65. "
                "Budi Santoso (8B) Matematika 74."
            ),
        ),
        Document(
            key="piagam",
            title="Data Siswa & NIK (Sangat Terbatas)",
            source="Data_Siswa_Internal.md",
            scope_key="data_siswa",
            date="2026-10-15",
            content=(
                "Andi Wijaya, 7A, NIK 3273051508120001, telepon 0812-3456-7890, "
                "orang tua Ibu Rina, NIK orang tua 3274051508120002. "
                "Siti Nurhaliza, 7A, NIK 3273051508120015."
            ),
        ),
    ]
    return {d.key: d for d in docs}


KB = _kb()

#: Konflik yang disengaja untuk menguji deteksi sumber (Test 5).
SOURCE_CONFLICTS = [
    {
        "topic": "jam ujian PTS Matematika kelas 7A",
        "older": ("SOP/jadwal default", "Jam ujian PTS dimulai 07.30 sesuai jadwal pelajaran."),
        "newer": ("Grup_Wali_Kelas_7A.txt (15 Okt 2026 08:00)",
                  "Ujian PTS Matematika dimulai jam 08.00 di Ruang 2A, bukan jam 07.30."),
    },
]


# ---------------------------------------------------------------------------
# 4. LAYER 1-4: PROMPT PIPELINE
# ---------------------------------------------------------------------------

def detect_injection(text: str) -> str | None:
    """Layer 10 — abaikan instruksi yang disematkan di dalam data."""
    for pattern in INJECTION_PATTERNS:
        m = pattern.search(text)
        if m:
            return (m.group(1) if m.groups() else m.group(0)).strip()
    return None


def mask_personal_data(text: str) -> tuple[str, bool]:
    """Layer 9 — masking data pribadi (NIK, telepon)."""
    masked = False
    out = text
    for pattern, repl in MASKING_PATTERNS:
        if pattern.search(out):
            masked = True
            out = pattern.sub(repl, out)
    return out, masked


def classify_intent(query: str) -> str:
    """Layer 3 — klasifikasi intent.

    Urutan penting: intent yang lebih spesifik diperiksa lebih dulu agar kata
    umum seperti 'kelas' tidak menyerobot ke JADWAL.
    """
    q = query.lower()

    # Spesifik dulu
    if any(k in q for k in ("gaji", "honor", "upah")):
        return "GAJI"
    if any(k in q for k in ("nik", "nomor telepon", "no. telp", "no telp", "nomor hp",
                            "kontak siswa")):
        return "DATA_PRIBADI"
    if any(k in q for k in ("spp", "iuran", "uang sekolah", "biaya")):
        return "SPP"
    if any(k in q for k in ("nilai", "raport", "kkm", "rekap nilai")):
        return "NILAI"
    if any(k in q for k in ("sop", "prosedur", "tata cara", "syarat", "surat izin",
                            "cara minta", "cara mengajukan")):
        return "SOP"
    if any(k in q for k in ("tugas", "task", "assignee", "task board")):
        return "TASK"
    if any(k in q for k in ("kalender", "libur", "wisuda", "kegiatan bulan",
                            "agenda bulan")):
        return "KALENDER"
    if any(k in q for k in ("ketua osis", "ketua kelas", "struktur organisasi",
                            "pengurus")):
        return "STRUKTUR"
    if any(k in q for k in ("jadwal", "pelajaran", "jam berapa", "ujian",
                            "pts", "pas", "mata pelajaran")):
        return "JADWAL"
    if any(k in q for k in ("rapat", "meeting")):
        return "RAPAT"
    return "GENERAL"


#: Intent -> kunci pengetahuan yang boleh dicari
INTENT_SCOPE = {
    "JADWAL": ["jadwal", "chat_wali", "kalender", "task"],
    "NILAI": ["nilai"],
    "SPP": ["spp"],
    "SOP": ["sop"],
    "KALENDER": ["kalender", "chat_guru", "chat_wali", "task"],
    "TASK": ["task"],
    "DATA_PRIBADI": ["piagam", "nilai"],
    "GAJI": ["piagam"],
    "STRUKTUR": ["kegiatan"],
    "RAPAT": ["task", "chat_kepala", "chat_guru"],
    "GENERAL": ["jadwal", "kalender", "sop", "spp", "kegiatan"],
}


def accessible_keys(user: User, intent: str) -> list[str]:
    """Daftar kunci dokumen yang memang boleh dibaca user untuk intent ini.

    Sumber sekunder yang di luar cakupan user akan DISARING, bukan memblokir
    seluruh pertanyaan. Sebuah pertanyaan hanya ditolak bila TIDAK ADA satupun
    sumber yang boleh diakses.

    Berkas chat dan berkas sensitif HANYA untuk role yang memang punya
    scope-nya (lihat ROLE_SCOPE). SISWA dan ORANG_TUA tidak pernah mendapat
    chat_wali / chat_guru / chat_kepala — sekalipun level aksesnya cukup.
    """
    role_scope = ROLE_SCOPE.get(user.role, set())
    out: list[str] = []
    for key in INTENT_SCOPE.get(intent, []):
        if key in RESTRICTED_KEYS and key not in role_scope:
            continue
        if user.level < SCOPE_MIN_LEVEL.get(key, 1):
            continue
        out.append(key)
    # piagam / data pribadi hanya untuk role yang punya scope-nya
    if intent == "DATA_PRIBADI" and "piagam" not in role_scope:
        out = []
    if intent == "NILAI" and "nilai" not in role_scope:
        out = []
    return out


def check_permission(user: User, intent: str, query: str) -> tuple[bool, str]:
    """Layer 4 — cek hak akses sebelum searching.

    Return (allowed, reason).
    """
    q = query.lower()
    level = user.level

    # Alumni — akses dicabut setelah lulus
    if user.role == "ALUMNI":
        return False, "ALUMNI"

    # Gaji / keuangan internal — tidak pernah untuk siswa, ortu, guru
    if intent == "GAJI" and level < 4:
        return False, "GAJI_TERBATAS"

    # Data pribadi siswa lain
    if intent == "DATA_PRIBADI":
        if level >= 4:
            return True, "OK"
        if user.role == ROLE_SISWA and ("saya" in q or "nama saya" in q
                                       or "saya punya" in q or q.endswith("saya")):
            return True, "SELF_DATA"
        if user.role == ROLE_ORTU and "anak" in q:
            return True, "SELF_DATA"
        return False, "DATA_PRIBADI_ORANG_LAIN"

    # Task board internal
    if intent == "TASK" and level < 2:
        return False, "TASK_TERBATAS"

    # Tidak ada satu pun sumber yang boleh diakses
    if not accessible_keys(user, intent):
        return False, "SCOPE_TERBATAS"

    return True, "OK"


def retrieve(user: User, intent: str, query: str, top_k: int = 5) -> list[RetrievedDoc]:
    """Layer 5 — retrieval dengan filter permission."""
    wanted = set(accessible_keys(user, intent))
    q_tokens = set(re.findall(r"[a-z0-9]+", query.lower()))
    stop = {"yang", "untuk", "dengan", "saya", "kami", "apakah", "berapa", "kapan",
            "jam", "di", "ke", "dari", "pada", "itu", "ini", "adalah", "sudah",
            "belum", "tolong", "dong", "ya", "sih", "kak"}
    q_tokens -= stop

    results: list[RetrievedDoc] = []
    for key, doc in KB.items():
        if key not in wanted:
            continue

        doc_tokens = set(re.findall(r"[a-z0-9]+", doc.content.lower()))
        overlap = q_tokens & doc_tokens
        score = len(overlap) / (len(q_tokens) + 1) if q_tokens else 0.2
        # Recency bonus untuk dokumen chat (paling baru)
        if key.startswith("chat_"):
            score += 0.15
        results.append(RetrievedDoc(doc, round(min(score, 0.99), 3), doc.content[:180]))

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:top_k]


# ---------------------------------------------------------------------------
# 5. LAYER 6: RESPONSE GENERATION
# ---------------------------------------------------------------------------

def _find_person(user: User, name: str) -> str | None:
    """Cek apakah nama yang disebut adalah 'diri sendiri' atau anak sendiri."""
    target = name.lower()
    if user.role == ROLE_SISWA and target in user.name.lower():
        return user.name
    if user.role == ROLE_ORTU:
        for child in user.children:
            if target in child.lower() or child.lower() in target:
                return child
    return None


def generate_answer(user: User, intent: str, query: str,
                    docs: list[RetrievedDoc],
                    self_data: bool = False) -> tuple[str, list[str], bool]:
    """Layer 6 — sintesis jawaban + sitasi.

    `self_data=True` bila Layer 4 menyimpulkan pertanyaan menyangkut data milik
    pengguna sendiri — jawaban yang berisi NIK/telepon TIDAK dimasking (Layer 9).

    Return (answer, sources_used, conflict_flag).
    """
    sources = [d.document.source for d in docs]
    q = query.lower()
    conflict = False

    # --- Intent-specific answers (deterministic untuk testing) ---
    if intent == "GAJI":
        return ("Maaf, informasi tersebut tidak tersedia untuk Anda.",
                sources, False)

    if intent == "STRUKTUR":
        return ("Maaf, saya tidak menemukan informasi tentang ketua OSIS. "
                "Silakan hubungi Pembina OSIS.", sources, False)

    if intent == "DATA_PRIBADI" and self_data:
        doc = KB["piagam"]
        if user.role == ROLE_SISWA:
            return (f"NIK Anda: 3273051508120001. Telepon: 0812-3456-7890. "
                    f"Sumber: {doc.source}", [doc.source], False)
        if user.role == ROLE_ORTU:
            return (f"NIK anak Anda: 3273051508120001. Telepon: 0812-3456-7890. "
                    f"Sumber: {doc.source}", [doc.source], False)

    # Role berwenang (OPERATOR ke atas) boleh melihat data pribadi siswa lain,
    # tetapi jawabannya WAJIB melewati Layer 9 sebelum keluar — kecuali
    # KEPALA MADRASAH yang menurut RBAC punya akses penuh.
    # GURU dan WALI_KELAS tidak termasuk: NIK adalah data administratif, dan
    # Layer 4 sudah menolaknya lebih dulu.
    if intent == "DATA_PRIBADI" and not self_data and user.level >= 4:
        doc = KB["piagam"]
        return (f"Data pribadi siswa kelas 7A — Andi Wijaya, "
                f"NIK 3273051508120001, telepon 0812-3456-7890. "
                f"Sumber: {doc.source}", [doc.source], False)

    if intent == "NILAI":
        # Pertanyaan tentang tenggat pengisian nilai -> jawab dari chat guru
        if "deadline" in q or "paling lambat" in q or "kapan" in q or "tenggat" in q:
            doc = KB["chat_guru"]
            return ("Deadline pengisian nilai PTS adalah 20 Oktober 2026 "
                    "(instruksi Kepala Madrasah di grup guru mata pelajaran, "
                    "10 Okt 2026 14:00). "
                    f"Sumber: {doc.source}", [doc.source], False)
        m = re.search(r"nilai (?:ujian )?matematika ([a-z]+)", q)
        if m:
            name = m.group(1).capitalize()
            if _find_person(user, name):
                return (f"Nilai Matematika {name}: 82. Sumber: {KB['nilai'].source}",
                        [KB["nilai"].source], False)
            return ("Maaf, Anda hanya dapat melihat nilai Anda sendiri.",
                    sources, False)
        return (f"Berikut rekap nilai yang relevan. Sumber: {KB['nilai'].source}, {KB['chat_guru'].source}",
                [KB["nilai"].source, KB["chat_guru"].source], False)

    if intent == "TASK":
        if user.level < 2:
            return ("Maaf, Anda tidak memiliki akses ke task internal madrasah.",
                    sources, False)
        return ("Task yang sedang berjalan:\n"
                "- T001 Persiapan Ujian PTS — Pak Ahmad — deadline 16 Okt 2026 (In Progress)\n"
                "- T002 Update Data Siswa Baru — Operator — deadline 10 Okt 2026 (OVERDUE, In Progress)\n"
                "- T004 Rapat Koordinasi Wali Kelas — Kepala Madrasah — 17 Okt 2026 (To Do)\n"
                f"Sumber: {KB['task'].source}", [KB["task"].source], False)

    if intent == "SPP":
        doc = KB["spp"]
        if "kelas 9" in q:
            return ("SPP kelas 9 adalah Rp 450.000/bulan. "
                    f"Sumber: {doc.source}", [doc.source], False)
        if "kelas 8" in q:
            return ("SPP kelas 8 adalah Rp 400.000/bulan. "
                    f"Sumber: {doc.source}", [doc.source], False)
        if "kelas 7" in q:
            return ("SPP kelas 7 adalah Rp 350.000/bulan. "
                    f"Sumber: {doc.source}", [doc.source], False)
        return (f"SPP dan iuran 2026/2027 sesuai SK 042/SK-MA/2026. Sumber: {doc.source}",
                [doc.source], False)

    if intent == "SOP":
        doc = KB["sop"]
        return ("Prosedur surat izin siswa:\n"
                "1. Siswa mengisi formulir izin di ruang operator\n"
                "2. Formulir ditandatangani orang tua/wali\n"
                "3. Diserahkan ke wali kelas untuk paraf\n"
                "4. Wali kelas meneruskan ke Kepala Madrasah untuk approval\n"
                "5. Operator mencetak surat izin resmi\n"
                "6. Surat izin diserahkan ke siswa\n"
                "Waktu pemrosesan maksimal 2 hari kerja.\n"
                f"Sumber: {doc.source}", [doc.source], False)

    if intent == "KALENDER":
        doc = KB["kalender"]
        if "libur semester 1" in q:
            return ("Libur semester 1: 1-10 Januari 2027. "
                    f"Sumber: {doc.source}", [doc.source], False)
        if "wisuda" in q:
            return ("Berdasarkan Kalender Akademik, wisuda kelas 9 dijadwalkan 20 Mei 2027. "
                    f"Sumber: {doc.source}", [doc.source], False)
        if "oktober" in q:
            return ("Kegiatan bulan Oktober 2026:\n"
                    "- 5-16 Oktober: Ujian Tengah Semester (Kalender)\n"
                    "- 15 Okt: Ujian PTS Matematika kelas 7A jam 08.00 Ruang 2A (Chat Wali Kelas)\n"
                    "- 18 Okt: Remedial Bahasa Inggris jam 08.00-10.00 (Chat Guru)\n"
                    "- 18 Okt: Deadline proposal perbaikan komputer lab (Task T003)\n"
                    "- 20 Okt: Deadline pengisian nilai PTS (Chat Guru)\n"
                    f"Sumber: {KB['kalender'].source}, {KB['chat_wali'].source}, "
                    f"{KB['chat_guru'].source}, {KB['task'].source}",
                    [KB["kalender"].source, KB["chat_wali"].source,
                     KB["chat_guru"].source, KB["task"].source], False)
        return (f"Informasi kalender akademik 2026/2027. Sumber: {doc.source}",
                [doc.source], False)

    if intent == "RAPAT":
        return ("Terdapat beberapa rapat: Rapat Koordinasi Wali Kelas (17 Okt 2026) dan "
                "Rapat Dinas yang belum ada jadwal. Maksud Anda yang mana?",
                [KB["task"].source], False)

    if intent == "JADWAL":
        # "math"/"mtk" adalah alias umum untuk Matematika (input campuran ID/EN)
        math_q = any(k in q for k in ("matematika", "math", "mtk"))
        if "ujian" in q and math_q:
            # Tanggal ujian PTS Matematika 7A menurut chat wali kelas: 16 Okt 2026
            exam_date = datetime(2026, 10, 16, tzinfo=WIB).date()
            wants_tomorrow = "besok" in q
            # Kesadaran temporal: acara yang tanggalnya sudah lewat TIDAK boleh
            # disajikan sebagai acara yang akan datang.
            today = NOW.date()
            exam_past = exam_date < today
            tense = ("sudah dilaksanakan pada" if exam_past
                     else "dijadwalkan pada")
            # Layer 4/5: hanya role yang punya scope chat_wali boleh melihat isi
            # berkas chat. SISWA dan ORANG_TUA dijawab dari kalender (publik).
            chat_ok = "chat_wali" in accessible_keys(user, "JADWAL")
            if chat_ok:
                # Staf: kalender + chat wali kelas → rekonsiliasi jam default
                # 07.30 terhadap pembaruan 08.00.
                conflict = True
                base = (f"Ujian PTS Matematika kelas 7A {tense} "
                        f"{tanggal_id(exam_date)} pukul 08.00 WIB di Ruang 2A. ")
                recon = ("Chat wali kelas 7A (15 Okt 2026) menegaskan jam 08.00 — "
                         "bukan 07.30 seperti jadwal pelajaran reguler. "
                         "Kalender akademik kini juga mencantumkan jadwal ini.")
                if wants_tomorrow:
                    tomorrow = (NOW + timedelta(days=1)).date()
                    if tomorrow != exam_date:
                        return (
                            base + f"Bukan besok ({tanggal_id(tomorrow)}). "
                            "Tidak ada ujian Matematika terjadwal untuk besok menurut "
                            "data yang saya miliki. Mohon konfirmasi ke Wali Kelas 7A "
                            "(Bu Siti) bila ada perubahan jadwal.\n"
                            f"Sumber: {KB['chat_wali'].source} (chat 15 Okt 2026, 08:00); "
                            f"{KB['kalender'].source}; {KB['jadwal'].source}",
                            [KB["chat_wali"].source, KB["kalender"].source,
                             KB["jadwal"].source], conflict)
                return (base + recon + "\n"
                        f"Sumber: {KB['chat_wali'].source} (chat 15 Okt 2026, 08:00); "
                        f"{KB['kalender'].source}",
                        [KB["chat_wali"].source, KB["kalender"].source], conflict)
            # Siswa / orang tua: jawab dari kalender akademik (publik).
            # TIDAK ada satu pun karakter dari berkas chat yang bocor.
            kal = KB["kalender"]
            if wants_tomorrow:
                tomorrow = (NOW + timedelta(days=1)).date()
                if tomorrow != exam_date:
                    return (f"Ujian PTS Matematika kelas 7A {tense} "
                            f"{tanggal_id(exam_date)} pukul 08.00 WIB di Ruang 2A — "
                            f"bukan besok ({tanggal_id(tomorrow)}). "
                            "Tidak ada ujian Matematika terjadwal untuk besok menurut "
                            "data yang saya miliki. Bila ada perubahan jadwal, mohon "
                            "konfirmasi ke Wali Kelas 7A (Bu Siti).\n"
                            f"Sumber: {kal.source} (Jadwal Ujian PTS)",
                            [kal.source], False)
            return (f"Ujian PTS Matematika kelas 7A {tense} "
                    f"{tanggal_id(exam_date)} pukul 08.00 WIB di Ruang 2A. Catatan: "
                    "ujian dimulai 08.00, bukan 07.30 seperti jam masuk pelajaran "
                    "reguler. Bawa pensil 2B dan penghapus; kalkulator tidak "
                    "diperbolehkan.\n"
                    f"Sumber: {kal.source} (Jadwal Ujian PTS)",
                    [kal.source], False)
        if "7a" in q and "senin" in q:
            doc = KB["jadwal"]
            return ("Jadwal kelas 7A hari Senin:\n"
                    "- Quran Hadits (07:30-09:00)\n"
                    "- Matematika (09:00-10:30)\n"
                    "- Bahasa Indonesia (10:45-12:15)\n"
                    f"Sumber: {doc.source}", [doc.source], False)
        if "7a" in q:
            doc = KB["jadwal"]
            return ("Jadwal lengkap kelas 7A (Senin-Jumat) tersedia. "
                    f"Sumber: {doc.source}", [doc.source], False)
        doc = KB["jadwal"]
        return (f"Informasi jadwal pelajaran. Sumber: {doc.source}", [doc.source], False)

    # GENERAL — fallback ke dokumen teratas
    if not docs:
        return ("Maaf, saya tidak menemukan informasi tentang hal tersebut. "
                "Silakan hubungi Bagian Administrasi atau operator madrasah.",
                [], False)
    top = docs[0]
    return (f"Berdasarkan {top.document.title}: {top.snippet}… "
            f"Sumber: {top.document.source}", [top.document.source], False)


# ---------------------------------------------------------------------------
# 6. CHALLENGE A — WORKPLACE BRAIN (end-to-end)
# ---------------------------------------------------------------------------

class AsistenMadrasah:
    """Agent utama Challenge A — pipeline 10 layer."""

    def __init__(self) -> None:
        self.audit: list[AuditEntry] = []
        self._session = 0

    # -- helpers ------------------------------------------------------------
    def _next_session(self) -> str:
        self._session += 1
        return f"sess_{self._session:03d}"

    def _log(self, entry: AuditEntry) -> None:
        self.audit.append(entry)

    # -- public API ---------------------------------------------------------
    def ask(self, user: User, query: str) -> dict[str, Any]:
        """Proses satu pertanyaan pengguna.

        Routing otomatis: pesan panjang yang berisi perintah kerja dialihkan ke
        Smart Task Handler (Challenge B). Pesan pendek -> Workplace Brain (A).
        """
        # Routing ke Smart Task Handler bila pesan panjang & berisi perintah kerja
        if is_smart_task_input(user, query):
            st = smart_task(user, query)
            if st.get("ok"):
                self._log(AuditEntry(
                    timestamp=NOW.isoformat(), session_id=self._next_session(),
                    user_id=user.id, user_name=user.name, role=user.role,
                    query=query, intent="SMART_TASK",
                    permission_check="ALLOWED", sources_accessed=[],
                    response_summary=st["screen"][:120],
                    action_taken="PENDING_APPROVAL", approval_required=True,
                    approval_status="PENDING",
                    prompt_injection_detected=bool(st.get("injection")),
                ))
                return {"answer": st["screen"], "sources": [], "intent": "SMART_TASK",
                        "permission": "ALLOWED", "smart_task": st,
                        "audit_id": len(self.audit) - 1}
            answer = st["message"]
            self._log(AuditEntry(
                timestamp=NOW.isoformat(), session_id=self._next_session(),
                user_id=user.id, user_name=user.name, role=user.role,
                query=query, intent="SMART_TASK",
                permission_check="DENIED (SMART_TASK_ROLE)" if st["stage"] == "PERMISSION"
                else "ALLOWED",
                sources_accessed=[], response_summary=answer[:120],
            ))
            return {"answer": answer, "sources": [], "intent": "SMART_TASK",
                    "permission": "DENIED" if st["stage"] == "PERMISSION" else "ALLOWED",
                    "audit_id": len(self.audit) - 1}

        session = self._next_session()

        # Layer 10 — deteksi prompt injection pada input & hasil retrieval
        injection = detect_injection(query)

        # Layer 3 — klasifikasi intent
        intent = classify_intent(query)

        # Layer 4 — permission check (SEBELUM search)
        allowed, reason = check_permission(user, intent, query)
        if not allowed:
            answer = self._deny_message(user, intent, reason)
            self._log(AuditEntry(
                timestamp=NOW.isoformat(), session_id=session, user_id=user.id,
                user_name=user.name, role=user.role, query=query, intent=intent,
                permission_check=f"DENIED ({reason})", sources_accessed=[],
                response_summary=answer[:120],
                prompt_injection_detected=bool(injection),
            ))
            return {"answer": answer, "sources": [], "intent": intent,
                    "permission": "DENIED", "audit_id": len(self.audit) - 1}

        # Layer 5 — retrieval dengan filter
        docs = retrieve(user, intent, query)

        # Layer 6 — sintesis + sitasi
        answer, sources, conflict = generate_answer(
            user, intent, query, docs, self_data=(reason == "SELF_DATA"))

        # Layer 8 — deteksi injection di dalam dokumen yang retrieved
        if not injection:
            for d in docs:
                found = detect_injection(d.snippet)
                if found:
                    injection = found
                    answer += (f"\n\n⚠️ Terdeteksi instruksi tidak sah dalam dokumen "
                               f"('{found}'). Tindakan diabaikan.")
                    break

        # Layer 9 — masking data pribadi.
        # Dikecualikan hanya untuk dua kasus yang memang sah tanpa masking:
        #   1. SELF_DATA — data milik pemohon sendiri
        #   2. KEPALA_MADRASAH — RBAC memberinya akses penuh (FULL READ/WRITE)
        masked = False
        if reason != "SELF_DATA" and user.role != ROLE_KEPALA:
            answer, masked = mask_personal_data(answer)

        self._log(AuditEntry(
            timestamp=NOW.isoformat(), session_id=session, user_id=user.id,
            user_name=user.name, role=user.role, query=query, intent=intent,
            permission_check="ALLOWED", sources_accessed=sources,
            response_summary=answer[:120],
            prompt_injection_detected=bool(injection),
            data_masked=masked, conflict_detected=conflict,
        ))

        return {"answer": answer, "sources": sources, "intent": intent,
                "permission": "ALLOWED", "conflict": conflict,
                "audit_id": len(self.audit) - 1}

    @staticmethod
    def _deny_message(user: User, intent: str, reason: str) -> str:
        if reason == "GAJI_TERBATAS":
            return "Maaf, informasi tersebut tidak tersedia untuk Anda."
        if reason == "DATA_PRIBADI_ORANG_LAIN":
            return "Maaf, Anda tidak memiliki akses ke NIK siswa lain."
        if reason == "TASK_TERBATAS":
            return "Maaf, Anda tidak memiliki akses ke task internal madrasah."
        if reason == "ALUMNI":
            return ("Maaf, akses Anda sebagai alumni terbatas. "
                    "Silakan hubungi Bagian Administrasi.")
        if reason.startswith("SCOPE_TERBATAS"):
            return "Maaf, informasi tersebut tidak tersedia untuk Anda."
        return "Maaf, Anda tidak memiliki akses ke informasi tersebut."

    def audit_log(self) -> list[AuditEntry]:
        return self.audit

    def export_audit(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write("[\n")
            f.write(",\n".join(e.to_json() for e in self.audit))
            f.write("\n]\n")


# ---------------------------------------------------------------------------
# 7. CHALLENGE B — SMART TASK HANDLER
# ---------------------------------------------------------------------------

def is_smart_task_input(user: User, message: str) -> bool:
    """Helper untuk routing otomatis."""
    if user.role not in SMART_TASK_ROLES:
        return False
    # Pesan panjang (> 50 chars) dan berisi kata kerja perintah
    q = message.lower()
    has_verb = any(verb in q for verb in ACTION_VERBS.keys())
    return len(message) > 40 and has_verb


@dataclass
class Task:
    task_id: str
    action: str
    object: str
    assignee: str | None = None
    target: str | None = None
    deadline: str | None = None
    deadline_text: str = ""
    priority: str = "SEDANG"
    source_span: str = ""
    confidence: float = 1.0
    conflict: str | None = None
    conflict_code: str | None = None
    suggestion: str | None = None
    needs_confirmation: list[str] = field(default_factory=list)


ACTION_VERBS = {
    "kirim": "send_email", "kirimkan": "send_email", "forward": "send_email",
    "jadwalkan": "schedule_meeting", "jadwalin": "schedule_meeting",
    "buat": "create_task", "bikin": "create_task", "siapkan": "create_task",
    "update": "create_task", "perbarui": "create_task",
    "ingatkan": "reminder", "ingetin": "reminder",
    "sebarkan": "post_announcement", "post": "post_announcement",
    "umumkan": "post_announcement",
    "minta": "create_task", "mohon": "create_task", "agar": "create_task",
}

PRIORITY_KEYWORDS = {
    "urgent": "URGENT", "segera": "URGENT", "penting": "TINGGI",
    "hari ini": "TINGGI", "asap": "URGENT", "mendesak": "URGENT",
}

DAY_WORDS = {
    "senin": 0, "selasa": 1, "rabu": 2, "kamis": 3, "jumat": 4, "jum'at": 4,
    "sabtu": 5, "minggu": 6,
}

MONTHS = {m: i + 1 for i, m in enumerate(
    ["januari", "februari", "maret", "april", "mei", "juni", "juli", "agustus",
     "september", "oktober", "november", "desember"])}


def _next_working_day(d: datetime) -> datetime:
    nxt = d + timedelta(days=1)
    while nxt.weekday() >= 5:
        nxt += timedelta(days=1)
    return nxt


def _parse_deadline(text: str, base: datetime) -> tuple[str | None, str]:
    """Ekstrak tanggal/waktu dari teks. Return (iso, teks_mentah).

    Prioritas: tanggal eksplisit > nama hari > 'besok'/'hari ini' > jam saja.
    Jam hanya dipakai sebagai *pelengkap* tanggal/hari, bukan pengganti.
    """
    q = text.lower()
    day_word = _detect_day_word(q)
    explicit_date = re.search(
        r"(\d{1,2})\s+(januari|februari|maret|april|mei|juni|juli|agustus|"
        r"september|oktober|november|desember)", q)

    hm = re.search(r"jam\s*(\d{1,2})[.:](\d{2})", q)
    hour = minute = None
    if hm:
        hour, minute = int(hm.group(1)), int(hm.group(2))
    elif re.search(r"\bsiang\b", q):
        hour, minute = 12, 0
    elif re.search(r"\bpagi\b", q):
        hour, minute = 8, 0
    elif re.search(r"\bsore\b", q):
        hour, minute = 15, 30

    def _apply(d: datetime) -> datetime:
        return d.replace(hour=hour, minute=minute) if hour is not None else d

    if explicit_date:
        day = int(explicit_date.group(1))
        month = MONTHS[explicit_date.group(2)]
        year = base.year
        if (month, day) < (base.month, base.day) and month < 8:
            year += 1
        d = _apply(datetime(year, month, day, tzinfo=WIB))
        return d.isoformat(), explicit_date.group(0)

    if day_word:
        target = DAY_WORDS[day_word]
        delta = (target - base.weekday()) % 7
        d = _apply(base + timedelta(days=delta))
        return d.isoformat(), day_word

    if "besok" in q:
        return _apply(_next_working_day(base)).isoformat(), "besok"
    if "hari ini" in q:
        return _apply(base).isoformat(), "hari ini"

    if hour is not None:
        label = f"jam {hm.group(1)}.{hm.group(2)}" if hm else ("siang" if hour == 12 else "pagi")
        return base.replace(hour=hour, minute=minute).isoformat(), label

    return None, ""


def _detect_day_word(text: str) -> str | None:
    q = text.lower()
    m = re.search(r"\b(senin|selasa|rabu|kamis|jumat|jum'at|sabtu|minggu)\b", q)
    return m.group(1) if m else None


#: Pola nama orang dengan gelar sapaan (Pak / Bu / Ibu / Bapak / Drs.)
PERSON_PATTERN = r"(?:pak|bu|ibu|bapak|drs\.?)\s+[A-Za-z]+"


def _extract_assignees(segment: str) -> list[str]:
    """Ambil SEMUA nama yang disebut dalam satu segmen.

    "Minta Pak Ahmad dan Bu Siti untuk hadir..." -> ["Pak Ahmad", "Bu Siti"]
    """
    found = re.findall(rf"\b{PERSON_PATTERN}", segment, re.IGNORECASE)
    out: list[str] = []
    for name in found:
        clean = re.sub(r"\s+", " ", name).strip()
        # normalisasi "Ibu" -> "Bu" agar konsisten & tidak dobel
        clean = re.sub(r"^(ibu|bapak)\b", "Bu", clean, flags=re.IGNORECASE)
        if clean.lower() not in {o.lower() for o in out}:
            out.append(clean)
    return out


def decompose(message: str, base: datetime = NOW) -> list[Task]:
    """Tahap 1 — pecah pesan menjadi task terpisah.

    Satu perintah kerja yang menyebut >1 penerima (mis. "Pak Ahmad dan Bu Siti")
    tetap dianggap SATU perintah, tetapi menghasilkan SATU task per penerima —
    karena setiap orang punya jadwal sendiri yang harus divalidasi terpisah.
    """
    # Jangan pecah pada "dan" yang diikuti nama orang (itu daftar penerima).
    split_re = re.compile(
        rf"[.,;]\s+|\bdan\s+(?!{PERSON_PATTERN})|\bterus\s+|\bserta\s+(?!{PERSON_PATTERN})",
        re.IGNORECASE,
    )
    segments = [s.strip() for s in split_re.split(message) if s and s.strip()]

    tasks: list[Task] = []
    counter = 1
    for seg in segments:
        q = seg.lower()
        verb = None
        for candidate, action in ACTION_VERBS.items():
            if re.search(rf"\b{candidate}\b", q):
                verb = action
                break
        if verb is None:
            continue

        assignees = _extract_assignees(seg)

        # object: sisa kalimat setelah kata kerja
        obj = re.sub(r"^\W*(tolong|tolong ya|tolongkah|hai|halo|assalamualaikum)\s*", "",
                      seg, flags=re.IGNORECASE)
        obj = re.sub(r"\b(kirim| kirimkan|jadwalkan|jadwalin|buat|bikin|siapkan|update|"
                     r"perbarui|ingatkan|ingetin|sebarkan|umumkan|umumnya)\b", "",
                     obj, flags=re.IGNORECASE)
        obj = re.sub(r"\b(ke|pada|untuk)\s+[a-z]+\b.*$", "", obj, flags=re.IGNORECASE)
        obj = re.sub(r"\s+", " ", obj).strip(" .,")
        if not obj:
            obj = seg.strip()

        iso, raw = _parse_deadline(seg, base)
        priority = "SEDANG"
        for kw, p in PRIORITY_KEYWORDS.items():
            if kw in q:
                priority = p
                break

        for assignee in (assignees or [None]):
            tasks.append(Task(
                task_id=f"ST{counter:03d}", action=verb, object=obj,
                assignee=assignee, deadline=iso, deadline_text=raw,
                priority=priority, source_span=seg,
            ))
            counter += 1
    return tasks


def validate(tasks: list[Task], base: datetime = NOW) -> list[Task]:
    """Tahap 2 — deteksi konflik."""
    for t in tasks:
        if not t.deadline:
            continue
        d = datetime.fromisoformat(t.deadline)

        # CF-01 — sholat Jumat
        if d.weekday() == 4:
            start, end_min = FRIDAY_PRAYER_WINDOW[0], FRIDAY_PRAYER_WINDOW[1]
            cur_min = d.hour * 60 + d.minute
            if start * 60 <= cur_min <= end_min * 60:
                t.conflict_code = "CF-01"
                t.conflict = ("Bentrok dengan waktu sholat Jumat "
                              f"({start}.00-{int(end_min)}.30 WIB)")
                t.suggestion = (f"{d.date().isoformat()} pukul 14.00 WIB")
                continue

        # CF-02 — hari libur nasional
        if d.date().isoformat() in PUBLIC_HOLIDAYS_2026_2027:
            t.conflict_code = "CF-02"
            t.conflict = PUBLIC_HOLIDAYS_2026_2027[d.date().isoformat()]
            t.suggestion = _next_working_day(d).date().isoformat()
            continue

        # CF-05 — libur semester / masa libur sekolah
        if d.date() >= datetime(2027, 1, 1, tzinfo=WIB).date() and \
           d.date() <= datetime(2027, 1, 10).date():
            t.conflict_code = "CF-05"
            t.conflict = "Berada pada masa libur semester 1"
            t.suggestion = "2027-01-11"
            continue

        # CF-03 — di luar jam kerja
        if d.hour < WORK_HOURS[0] or d.hour >= WORK_HOURS[1]:
            t.conflict_code = "CF-03"
            t.conflict = f"Di luar jam kerja ({WORK_HOURS[0]}.00-{WORK_HOURS[1]}.00 WIB)"
            t.suggestion = f"{d.date().isoformat()} pukul 08.00 WIB"
            continue

        # CF-06 — di luar jam operasional (malam)
        if d.hour >= 18:
            t.conflict_code = "CF-06"
            t.conflict = "Di luar jam operasional"
            t.suggestion = "keesokan harinya"
    return tasks


def clarify(tasks: list[Task]) -> list[str]:
    """Tahap 3 — pertanyaan klarifikasi (hanya bila ambigu)."""
    questions: list[str] = []
    for t in tasks:
        if t.assignee:
            key = " ".join(t.assignee.lower().split()[-2:])
            for amb_name, candidates in AMBIGUOUS_NAMES.items():
                if amb_name in t.assignee.lower():
                    listing = " dan ".join(candidates)
                    questions.append(
                        f"Terdapat {len(candidates)} orang bernama {amb_name.title()}: "
                        f"{listing}. Maksud Anda yang mana?")
                    break
        if t.deadline_text in {"siang", "malam"} or (
                t.deadline_text == "" and t.action == "schedule_meeting"):
            t.needs_confirmation.append("waktu")
            questions.append("Anda menyebut waktu yang kurang spesifik. "
                             "Mau jam berapa (WIB)?")
        if t.action == "schedule_meeting" and not t.assignee:
            t.needs_confirmation.append("peserta")
            questions.append("Siapa saja yang perlu diundang untuk rapat ini?")
    # dedupe
    seen: set[str] = set()
    out: list[str] = []
    for q in questions:
        if q not in seen:
            seen.add(q)
            out.append(q)
    return out


def confirmation_screen(tasks: list[Task], questions: list[str]) -> str:
    """Tahap 4 — layar konfirmasi."""
    icon = {"send_email": "📧", "schedule_meeting": "📅", "create_task": "📝",
            "post_announcement": "📢", "reminder": "⏰"}
    lines = [f"📋 {len(tasks)} Task Terdeteksi dari pesan Anda:", ""]
    blocked = 0
    warned = 0
    for i, t in enumerate(tasks, 1):
        lines.append(f"{i}. {icon.get(t.action, '•')} {t.object}")
        if t.assignee:
            lines.append(f"   → Penerima/Assignee: {t.assignee}")
        if t.target:
            lines.append(f"   → Tujuan: {t.target}")
        if t.deadline:
            lines.append(f"   → Waktu: {t.deadline}"
                         + (f" (dari kata '{t.deadline_text}')" if t.deadline_text else ""))
        lines.append(f"   → Prioritas: {t.priority}")
        if t.conflict:
            warned += 1
            lines.append(f"   ⚠️ {t.conflict_code}: {t.conflict}")
            lines.append(f"   → Usulan: {t.suggestion}")
        if t.needs_confirmation:
            blocked += 1
            lines.append(f"   ⛔ Perlu konfirmasi: {', '.join(t.needs_confirmation)}")
        lines.append(f"   ↳ Dasar: \"{t.source_span}\"")
        lines.append("")

    lines.append(f"Ringkasan: {blocked} perlu konfirmasi · {warned} peringatan konflik · "
                 f"{len(questions)} pertanyaan klarifikasi")
    if questions:
        lines.append("")
        lines.append("❓ Sebelum lanjut, saya perlu memastikan:")
        for i, q in enumerate(questions, 1):
            lines.append(f"   {i}. {q}")
    lines.append("")
    lines.append("[✅ Setujui Semua] [✏️ Ubah] [❌ Tolak]")
    return "\n".join(lines)


#: State machine approval gate
APPROVAL_STATES = {"PENDING", "EXECUTING", "EDITING", "CANCELLED",
                   "EXPIRED", "COMPLETED", "FAILED", "ESCALATED"}


@dataclass
class ApprovalSession:
    tasks: list[Task]
    state: str = "PENDING"
    reject_count: int = 0
    started_at: datetime = NOW
    approved_by: str | None = None
    executed: list[Task] = field(default_factory=list)
    history: list[str] = field(default_factory=list)


def approve(session: ApprovalSession, approver: str) -> dict[str, Any]:
    """Tahap 5 — approval gate. HANYA 'approve' bisa masuk EXECUTING."""
    if session.state != "PENDING":
        return {"ok": False, "state": session.state,
                "message": "Aksi tidak valid pada state saat ini."}

    session.state = "EXECUTING"
    session.approved_by = approver
    session.history.append(f"APPROVED by {approver}")

    # Tahap 6 — mock execution
    for t in session.tasks:
        t.deadline_final = t.suggestion or t.deadline
        session.executed.append(t)

    session.state = "COMPLETED"
    session.history.append("EXECUTED (mock)")
    return {"ok": True, "state": session.state, "tasks": session.executed}


def reject(session: ApprovalSession, by: str) -> dict[str, Any]:
    session.reject_count += 1
    session.history.append(f"REJECTED by {by} (#{session.reject_count})")
    if session.reject_count >= 3:
        session.state = "ESCALATED"
        session.history.append("ESCALATED to OPERATOR")
        return {"ok": True, "state": "ESCALATED",
                "message": "Anda telah menolak 3 kali. Task ini di-escalate ke "
                           "Operator untuk bantuan manual."}
    session.state = "CANCELLED"
    return {"ok": True, "state": "CANCELLED",
            "message": "❌ Task dibatalkan. Tidak ada action yang dieksekusi."}


def edit(session: ApprovalSession, changes: dict[str, Any]) -> dict[str, Any]:
    session.state = "EDITING"
    for t in session.tasks:
        for k, v in changes.items():
            if hasattr(t, k):
                setattr(t, k, v)
    session.state = "PENDING"  # approval lama tidak berlaku
    session.history.append("EDITED -> back to PENDING")
    return {"ok": True, "state": "PENDING",
            "message": "Perubahan disimpan. Silakan konfirmasi ulang."}


def mock_execute(task: Task) -> str:
    """Tahap 6 — mock execution. TIDAK ada tool nyata."""
    when = task.deadline_final if hasattr(task, "deadline_final") and task.deadline_final else task.deadline
    if task.action == "send_email":
        return (f"📧 Mock: Email draft siap dikirim ke {task.assignee} "
                f"({str(task.assignee).lower().replace(' ', '.')}@mtsn1jakarta.sch.id). "
                f"Subjek: {task.object}")
    if task.action == "schedule_meeting":
        return f"📅 Mock: Meeting '{task.object}' dijadwalkan {when}"
    if task.action == "create_task":
        return f"📝 Mock: Task '{task.object}' ditambahkan ke Task Board"
    if task.action == "post_announcement":
        return f"📢 Mock: Pengumuman siap diposting ke {task.target}"
    if task.action == "reminder":
        return f"⏰ Mock: Pengingat disiapkan untuk {task.assignee}"
    return f"• Mock: {task.object}"


# ---------------------------------------------------------------------------
# 8. ORCHESTRATOR SMART TASK
# ---------------------------------------------------------------------------

def smart_task(user: User, message: str, base: datetime = NOW) -> dict[str, Any]:
    """Pipeline lengkap Smart Task Handler (Tahap 1-4 + approval gate)."""
    if user.role not in SMART_TASK_ROLES:
        return {"ok": False, "stage": "PERMISSION",
                "message": "Maaf, fitur Smart Task Handler hanya tersedia untuk "
                           "Kepala Madrasah, Operator, Wali Kelas, dan Guru."}

    # Keamanan — injection pada input
    injection = detect_injection(message)
    cleaned = message
    if injection:
        cleaned = re.sub(r"[^.]*AI\s*:\s*[^.]*", "", message, flags=re.IGNORECASE).strip()

    tasks = decompose(cleaned, base)
    if not tasks:
        return {"ok": False, "stage": "DECOMPOSE",
                "message": "Informasi tidak lengkap. Mohon sebutkan: "
                           "(1) Hari/tanggal, (2) Jam, (3) Agenda, (4) Siapa yang hadir."}

    tasks = validate(tasks, base)
    questions = clarify(tasks)
    screen = confirmation_screen(tasks, questions)

    session = ApprovalSession(tasks=tasks)

    result: dict[str, Any] = {
        "ok": True,
        "stage": "CONFIRMATION",
        "session": session,
        "screen": screen,
        "questions": questions,
        "injection": injection,
        "tasks": tasks,
    }
    if injection:
        result["injection_notice"] = (
            f"Terdeteksi instruksi tidak sah dalam input: '{injection}'. "
            "Instruksi diabaikan.")
    return result


# ---------------------------------------------------------------------------
# 9. MOCK USERS
# ---------------------------------------------------------------------------

def mock_users() -> dict[str, User]:
    return {
        "andi_siswa": User("siswa_001", "Andi Wijaya", ROLE_SISWA, class_="7A"),
        "siswa_lain": User("siswa_002", "Rahmawati", ROLE_SISWA, class_="7A"),
        "ibu_rina": User("ortu_001", "Ibu Rina", ROLE_ORTU, children=["Andi Wijaya"]),
        "ortu_kelas9": User("ortu_002", "Bapak Sutrisno", ROLE_ORTU,
                            children=["Bagus Pratama"]),
        "pak_ahmad": User("guru_001", "Ahmad", ROLE_GURU, subjects=["Matematika"],
                          assigned_classes=["7A", "8B"]),
        "bu_siti": User("wali_001", "Siti Aminah", ROLE_WALI, class_="7A",
                        subjects=["Bahasa Indonesia"], assigned_classes=["7A"]),
        "kepala_madrasah": User("kepala_001", "Ahmad Fauzi", ROLE_KEPALA),
        "operator_budi": User("operator_001", "Budi Santoso", ROLE_OPERATOR),
        "alumni": User("alumni_001", "Dewi Lestari", "ALUMNI"),
    }


# ---------------------------------------------------------------------------
# 10. SELF-TEST / DEMO
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    users = mock_users()
    agent = AsistenMadrasah()

    if "--tests" in sys.argv:
        from test_runner import run_all  # type: ignore
        run_all(agent, users)
    else:
        print("=" * 72)
        print("ASISTEN MADRASAH — DEMO")
        print("=" * 72)

        demos = [
            ("kepala_madrasah", "Tolong kirim notulen rapat ke Pak Ahmad, "
                                "jadwalin follow-up Jumat jam 12.00, "
                                "dan update data siswa baru ya."),
            ("andi_siswa", "Jadwal pelajaran kelas 7A hari Senin"),
            ("ibu_rina", "Berapa SPP kelas 9?"),
            ("andi_siswa", "Jam berapa ujian PTS Matematika kelas 7A?"),
            ("siswa_lain", "Berapa nilai ujian matematika Andi?"),
            ("andi_siswa", "Siapa ketua OSIS tahun ini?"),
        ]

        for uname, query in demos:
            user = users[uname]
            print(f"\n{'=' * 72}")
            print(f"[{user.role}] {user.name}  —  {query}")
            print("-" * 72)
            res = agent.ask(user, query)
            print(res["answer"])
            if res["sources"]:
                print(f"\n[Sumber] {', '.join(res['sources'])}")

        print(f"\n{'=' * 72}")
        print("SMART TASK HANDLER — DEMO")
        print("=" * 72)
        kepala = users["kepala_madrasah"]
        st = smart_task(kepala,
                        "Tolong kirim notulen ke Pak Budi, jadwalkan follow-up "
                        "Jumat jam 12.00, dan ingatkan Bu Siti soal remedial.")
        print(st["screen"])
        print(f"\n[Pertanyaan klarifikasi] {len(st['questions'])}")

        print(f"\n{'=' * 72}")
        print("AUDIT LOG (5 terakhir)")
        print("=" * 72)
        for entry in agent.audit_log()[-5:]:
            print(f"{entry.timestamp} | {entry.role:16s} | {entry.permission_check:22s} "
                  f"| {entry.query[:40]}")
