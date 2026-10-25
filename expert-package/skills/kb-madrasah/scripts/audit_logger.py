"""Audit logger untuk Asisten Madrasah.

Menulis dan membaca audit log dalam format JSON Lines (satu entri per baris).
Menggantikan "Audit Log dashboard" yang tidak ada di WorkBuddy AI.

Pemakaian:
    python audit_logger.py append --json '{"role":"SISWA","intent":"SPP"}'
    python audit_logger.py read --role KEPALA_MADRASAH --today
    python audit_logger.py read --role OPERATOR --all
    python audit_logger.py summary
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

WIB = timezone(timedelta(hours=7))

SKILL_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = SKILL_DIR / "logs"
LOG_FILE = LOG_DIR / "audit.jsonl"

# Role yang boleh membaca seluruh log
FULL_ACCESS_ROLES = {"KEPALA_MADRASAH", "OPERATOR"}
# Role yang boleh membaca log miliknya sendiri saja
SELF_ONLY_ROLES = {"GURU", "WALI_KELAS"}
# Role tanpa akses log
NO_ACCESS_ROLES = {"SISWA", "ORANG_TUA", "ALUMNI"}

FIELDS = [
    "timestamp", "session_id", "user_id", "user_name", "role", "query",
    "intent", "permission_check", "sources_accessed", "response_summary",
    "action_taken", "approval_required", "approval_status",
    "prompt_injection_detected", "data_masked", "conflict_detected",
]

# Pola data sensitif yang harus selalu di-mask di dalam log
MASK_PATTERNS = [
    (re.compile(r"\b(\d{16})\b"), lambda m: m.group(1)[:4] + "*" * 8 + m.group(1)[-4:]),
    (re.compile(r"\b(08\d{2})[-\s]?(\d{3,4})[-\s]?(\d{3,4})\b"),
     lambda m: m.group(1) + "-****-" + m.group(3)),
]


def mask_text(text: str) -> tuple[str, bool]:
    """Mask NIK & nomor telepon di dalam teks. Kembalikan (teks, ada_yang_dimask)."""
    masked = False
    for pattern, repl in MASK_PATTERNS:
        new_text = pattern.sub(repl, text)
        if new_text != text:
            masked = True
            text = new_text
    return text, masked


def build_entry(payload: dict) -> dict:
    """Lengkapi payload menjadi entri audit dengan 16 field wajib."""
    now = datetime.now(WIB)
    query = str(payload.get("query", ""))
    summary = str(payload.get("response_summary", ""))

    masked_query, m1 = mask_text(query)
    masked_summary, m2 = mask_text(summary)

    entry = {
        "timestamp": now.isoformat(timespec="seconds"),
        "session_id": payload.get("session_id") or f"sess_{uuid.uuid4().hex[:12]}",
        "user_id": payload.get("user_id", "unknown"),
        "user_name": payload.get("user_name", "unknown"),
        "role": payload.get("role", "UNKNOWN"),
        "query": masked_query,
        "intent": payload.get("intent", "GENERAL"),
        "permission_check": payload.get("permission_check", "ALLOWED"),
        "sources_accessed": payload.get("sources_accessed", []),
        "response_summary": masked_summary,
        "action_taken": payload.get("action_taken", "NONE"),
        "approval_required": bool(payload.get("approval_required", False)),
        "approval_status": payload.get("approval_status", "N/A"),
        "prompt_injection_detected": bool(payload.get("prompt_injection_detected", False)),
        "data_masked": bool(payload.get("data_masked", m1 or m2)),
        "conflict_detected": bool(payload.get("conflict_detected", False)),
    }
    return entry


def cmd_append(args: argparse.Namespace) -> int:
    try:
        payload = json.loads(args.json)
    except json.JSONDecodeError as exc:
        print(f"❌ JSON tidak valid: {exc}", file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        print("❌ Payload harus berupa objek JSON.", file=sys.stderr)
        return 2

    entry = build_entry(payload)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"✅ Log ditambahkan ({entry['timestamp']}) — role={entry['role']} "
          f"intent={entry['intent']} perm={entry['permission_check']}")
    if entry["data_masked"]:
        print("   🔒 Data sensitif otomatis di-mask.")
    return 0


def _load_entries() -> list[dict]:
    if not LOG_FILE.exists():
        return []
    out = []
    with LOG_FILE.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"⚠️  Baris {line_no} rusak, dilewati.", file=sys.stderr)
    return out


def cmd_read(args: argparse.Namespace) -> int:
    role = args.role.upper()

    if role in NO_ACCESS_ROLES:
        print(f"❌ Akses ditolak. Role {role} tidak memiliki akses ke audit log.")
        return 1

    entries = _load_entries()

    if args.today:
        today = datetime.now(WIB).date().isoformat()
        entries = [e for e in entries if str(e.get("timestamp", "")).startswith(today)]

    if role in SELF_ONLY_ROLES:
        # Hanya log dengan role yang sama
        entries = [e for e in entries if e.get("role") == role]

    if not entries:
        print("(tidak ada entri log yang cocok)")
        return 0

    header = f"{'WAKTU':<20} {'ROLE':<16} {'INTENT':<11} {'PERM':<8} {'ACTION':<13} RINGKASAN"
    print(header)
    print("-" * len(header))
    for e in entries:
        ts = str(e.get("timestamp", ""))[11:19]
        perm = "ALLOWED" if str(e.get("permission_check", "")).startswith("ALLOWED") else "DENIED"
        summary = str(e.get("response_summary", ""))
        if len(summary) > 44:
            summary = summary[:43].rstrip() + "…"
        print(f"{ts:<20} {e.get('role', '-'):<16} {e.get('intent', '-'):<11} "
              f"{perm:<8} {e.get('action_taken', '-'):<13} {summary}")

    print(f"\nTotal: {len(entries)} entri (akses sebagai {role})")
    return 0


def cmd_summary(_: argparse.Namespace) -> int:
    entries = _load_entries()
    if not entries:
        print("(belum ada log)")
        return 0

    denied = sum(1 for e in entries
                 if not str(e.get("permission_check", "")).startswith("ALLOWED"))
    injections = sum(1 for e in entries if e.get("prompt_injection_detected"))
    masked = sum(1 for e in entries if e.get("data_masked"))
    conflicts = sum(1 for e in entries if e.get("conflict_detected"))
    approvals = sum(1 for e in entries if e.get("approval_required"))

    by_role: dict[str, int] = {}
    by_intent: dict[str, int] = {}
    for e in entries:
        by_role[e.get("role", "?")] = by_role.get(e.get("role", "?"), 0) + 1
        by_intent[e.get("intent", "?")] = by_intent.get(e.get("intent", "?"), 0) + 1

    print("=== RINGKASAN AUDIT ===")
    print(f"Total interaksi          : {len(entries)}")
    print(f"Akses ditolak            : {denied}")
    print(f"Prompt injection terdeteksi: {injections}")
    print(f"Data di-mask             : {masked}")
    print(f"Konflik sumber           : {conflicts}")
    print(f"Butuh approval           : {approvals}")
    print("\nPer role:")
    for role, count in sorted(by_role.items(), key=lambda kv: -kv[1]):
        print(f"  {role:<18} {count}")
    print("\nPer intent:")
    for intent, count in sorted(by_intent.items(), key=lambda kv: -kv[1]):
        print(f"  {intent:<18} {count}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit logger Asisten Madrasah (JSON Lines)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_append = sub.add_parser("append", help="tambah satu entri log")
    p_append.add_argument("--json", required=True, help="payload JSON satu baris")
    p_append.set_defaults(func=cmd_append)

    p_read = sub.add_parser("read", help="baca log sesuai hak akses role")
    p_read.add_argument("--role", required=True, help="role pembaca")
    group = p_read.add_mutually_exclusive_group()
    group.add_argument("--today", action="store_true", help="hanya hari ini")
    group.add_argument("--all", action="store_true", help="semua entri")
    p_read.set_defaults(func=cmd_read)

    p_summary = sub.add_parser("summary", help="ringkasan statistik log")
    p_summary.set_defaults(func=cmd_summary)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
