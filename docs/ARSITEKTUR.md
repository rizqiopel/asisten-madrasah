# Arsitektur Agent: Asisten Madrasah
## Challenge A — The Workplace Brain

---

## Diagram Arsitektur (Text-Based)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Web Chat   │  │ Mobile App  │  │  WhatsApp   │  │   Admin Dashboard   │ │
│  │  (Siswa)    │  │(Orang Tua)  │  │  (Guru)     │  │  (Kepala Madrasah)  │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         └─────────────────┴─────────────────┘                    │            │
│                           │                                      │            │
└───────────────────────────┼──────────────────────────────────────┼────────────┘
                            │                                      │
                            ▼                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AUTHENTICATION & RBAC                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  • Verify user identity (login/token)                                   │ │
│  │  • Check role: SISWA / ORANG_TUA / GURU / WALI_KELAS / KEPALA / OPERATOR│ │
│  │  • Load permission matrix for the role                                  │ │
│  │  • Log authentication event                                             │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         QUERY PROCESSOR                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Step 1: Parse query (Bahasa Indonesia / English / mixed)               │ │
│  │  Step 2: Classify intent (jadwal, nilai, SPP, SOP, task, general)       │ │
│  │  Step 3: Check permissions — can this role ask this?                    │ │
│  │  Step 4: If DENIED → return "Maaf, Anda tidak memiliki akses"           │ │
│  │  Step 5: If ALLOWED → route to Knowledge Engine                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        KNOWLEDGE ENGINE                                      │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │ Document Store  │  │  Chat Archive   │  │   Task Board    │              │
│  │  (SOP, Jadwal,  │  │  (Grup WA,      │  │  (Trello/Notion │              │
│  │   Kalender, SPP)│  │   Chat pribadi) │  │   style tasks)  │              │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘              │
│           │                    │                    │                        │
│           └────────────────────┼────────────────────┘                        │
│                                │                                             │
│                                ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                    SEARCH & RETRIEVAL MODULE                             │ │
│  │  • Semantic search across all data sources                              │ │
│  │  • Filter results by user permissions                                   │ │
│  │  • Rank by relevance & recency                                          │ │
│  │  • Detect conflicts between sources                                     │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      RESPONSE GENERATOR                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Step 1: Synthesize answer from retrieved sources                       │ │
│  │  Step 2: Add source citations (document name, page/section, date)       │ │
│  │  Step 3: If conflict detected → explain discrepancy & chosen source     │ │
│  │  Step 4: If no answer found → "Saya tidak tahu" + direct to SME        │ │
│  │  Step 5: Mask sensitive data (NIK, phone) if unauthorized               │ │
│  │  Step 6: Format response (structured, readable)                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      ACTION GATEWAY (For External Actions)                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  • Detect if query requires action (send email, book meeting, etc.)     │ │
│  │  • If NO action → return response directly                              │ │
│  │  • If action required → generate confirmation screen                    │ │
│  │  • Wait for human approval (YES/NO)                                     │ │
│  │  • If APPROVED → execute via mock/real tools                            │ │
│  │  • If REJECTED → cancel & log                                           │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   SMART TASK HANDLER (Challenge B Integration)               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Input: Chat/Voice note panjang dari Kepala/Operator/Guru               │ │
│  │  • Step 1: Decompose → pecah jadi task terpisah                         │ │
│  │  • Step 2: Extract → assignee, deadline, prioritas                      │ │
│  │  • Step 3: Clarify → tanya klarifikasi kalau ambigu                     │ │
│  │  • Step 4: Validate → cek konflik jadwal (Jumat siang = sholat)         │ │
│  │  • Step 5: Confirm → tampilkan ringkasan task                           │ │
│  │  • Step 6: Approve → tunggu human approval                              │ │
│  │  • Step 7: Execute → mock tools untuk demo                              │ │
│  │  • Access: KEPALA, OPERATOR, GURU only (Siswa/Ortu = DENY)              │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AUDIT LOGGER                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Log Entry Structure:                                                   │ │
│  │  {                                                                      │ │
│  │    timestamp: "2026-10-21T09:00:00+07:00",                              │ │
│  │    user_id: "siswa_001",                                                │ │
│  │    role: "SISWA",                                                       │ │
│  │    query: "Jadwal pelajaran hari Senin",                                │ │
│  │    sources_accessed: ["Jadwal_Pelajaran_Kelas_7_8_9.md"],               │ │
│  │    response_summary: "Jadwal kelas 7A Senin: Quran Hadits 07:30-09:00", │ │
│  │    action_taken: "NONE",                                                │ │
│  │    approval_required: false,                                            │ │
│  │    approval_status: "N/A"                                               │ │
│  │  }                                                                      │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYER                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  • Prompt Injection Detection: Scan documents for embedded instructions │ │
│  │  • Data Masking: Auto-mask NIK, phone numbers                           │ │
│  │  • Rate Limiting: Max 100 queries/minute per user                       │ │
│  │  • Input Sanitization: Remove malicious characters                      │ │
│  │  • Session Timeout: Auto-logout after 30 min idle                       │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Trust Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│  TRUST BOUNDARY 1: User Interface                           │
│  - Semua input dari user masuk di sini                      │
│  - Input di-sanitize sebelum diproses                       │
│  - Tidak ada data sensitif yang ditampilkan di UI           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  TRUST BOUNDARY 2: Authentication & RBAC                    │
│  - Gateway antara user dan data                             │
│  - Setiap query MESTI lewat permission check                │
│  - Tidak ada "shortcut" yang bypass RBAC                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  TRUST BOUNDARY 3: Knowledge Engine                         │
│  - Data di-filter berdasarkan role SEBELUM di-search        │
│  - Search hanya mengembalikan data yang diizinkan           │
│  - Source conflict detection di sini                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  TRUST BOUNDARY 4: Action Gateway                           │
│  - Semua action eksternal MESTI lewat approval              │
│  - Tidak ada action yang auto-execute                       │
│  - Mock tools untuk demo, real tools untuk production       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  TRUST BOUNDARY 5: Audit Logger                             │
│  - Immutable logs (tidak bisa di-edit)                      │
│  - Accessible only by Kepala Madrasah & Operator            │
│  - Encrypted at rest                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Design Trade-offs

| Trade-off | Decision | Rationale |
|-----------|----------|-----------|
| **Speed vs. Security** | Security first | Permission check dilakukan SEBELUM search, sedikit lebih lambat tapi aman |
| **Completeness vs. Privacy** | Privacy first | Kalau ragu, deny access. Lebih baik under-share than over-share |
| **Automation vs. Control** | Human-in-the-loop | Semua action eksternal butuh approval. Agent hanya retrieve & suggest |
| **Accuracy vs. Availability** | Accuracy first | "I don't know" lebih baik dari hallucination |
| **Complexity vs. Maintainability** | Maintainable | Arsitektur modular, tiap komponen bisa di-test & di-update independent |
| **Scope vs. Focus** | Focus + 1 feature | Core Workplace Brain + Smart Task Handler sebagai value-add |

---

## Smart Task Handler Flow

```
┌─────────────────────────────────────────────────────────────┐
│  INPUT: Voice Note / Chat Panjang                           │
│  "Tolong kirim notulen ke Pak Ahmad, jadwalin follow-up     │
│   Jumat siang, update data siswa baru."                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: DECOMPOSE                                          │
│  • Task 1: Kirim notulen ke Pak Ahmad                       │
│  • Task 2: Jadwalkan follow-up Jumat siang                  │
│  • Task 3: Update data siswa baru                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: EXTRACT & VALIDATE                                 │
│  • Task 1: Assignee = Pak Ahmad (Guru Matematika) ✓         │
│  • Task 2: Jumat siang → ⚠️  Konflik dengan sholat Jumat   │
│            → Usulkan: Jumat 14.00 WIB                       │
│  • Task 3: Assignee = Operator (default) ✓                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: CLARIFY (jika perlu)                               │
│  • "Pak Ahmad yang mana? Ada 2 Pak Ahmad di data."          │
│  • "Jumat siang = waktu sholat Jumat. Apakah 14.00 WIB?"    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: CONFIRMATION SCREEN                                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  3 Task Terdeteksi:                                 │    │
│  │  1. Kirim notulen ke Pak Ahmad (Guru Matematika)    │    │
│  │  2. Jadwalkan follow-up: Jumat, 24 Okt, 14.00 WIB   │    │
│  │  3. Update data siswa baru (Operator)               │    │
│  │                                                     │    │
│  │  [✅ Approve Semua]  [❌ Tolak]  [✏️ Edit]          │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: APPROVAL GATE                                      │
│  • User klik "Approve" → Execute via mock tools             │
│  • User klik "Tolak" → Cancel & log                         │
│  • User edit → Kembali ke Step 4                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: EXECUTE & LOG                                      │
│  • Mock: "Email draft siap dikirim ke Pak Ahmad"            │
│  • Mock: "Meeting 'Follow-up' dijadwalkan Jumat 14.00"      │
│  • Mock: "Task 'Update data siswa' ditambahkan ke board"    │
│  • Log: Semua action tercatat di Audit Logger               │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack (WorkBuddy)

| Komponen | WorkBuddy Feature |
|----------|-------------------|
| User Interface | WorkBuddy Chat (Expert Center) |
| Authentication | Prompt Layer 2 (RBAC 7 role) |
| Query Processor | Prompt Layering (10 layer) |
| Document Store | Skill `kb-madrasah` (Data mock) |
| Chat Archive | Skill `kb-madrasah` (Arsip txt) |
| Task Board | Skill `kb-madrasah` + `smart_task.py` |
| Response Generator | WorkBuddy LLM + Prompt Template |
| Action Gateway | Skill `smart_task.py` (Approval gate) |
| Audit Logger | Skill `audit_logger.py` (JSON Lines) |
| Security Layer | Prompt (Injection detection) + Sanitization |

---

*Arsitektur ini dirancang untuk accountability, security, dan auditability.
Dipetakan ke Expert Package v2.0 WorkBuddy. Last updated: 22 Oktober 2026*
