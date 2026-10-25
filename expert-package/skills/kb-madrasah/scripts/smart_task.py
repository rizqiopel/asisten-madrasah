"""CLI Smart Task Handler untuk Asisten Madrasah.

Membungkus logika di `asisten_madrasah.py` menjadi perintah yang bisa dipanggil
dari percakapan agent: decompose -> validate -> clarify -> confirmation screen ->
approval gate -> mock execution.

Pemakaian:
    python smart_task.py decompose --input "Kirim notulen ke Pak Ahmad, jadwalkan rapat Jumat siang"
    python smart_task.py validate  --file tasks.json
    python smart_task.py screen    --input "..."
    python smart_task.py approve   --file tasks.json --decision approve --by KEPALA_MADRASAH
    python smart_task.py conflicts
    python smart_task.py demo
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from asisten_madrasah import (  # noqa: E402
    NOW,
    ApprovalSession,
    User,
    approve,
    clarify,
    confirmation_screen,
    decompose,
    reject,
    smart_task,
    validate,
)

CONFLICT_CATALOG = [
    ("CF-01", "Jumat 11.00-13.30 WIB", "Bentrok sholat Jumat"),
    ("CF-02", "Hari libur nasional", "Madrasah tutup"),
    ("CF-03", "Di luar jam kerja 07.00-16.00", "Di luar jam operasional"),
    ("CF-04", "Penanggung jawab bentrok jadwal", "Assignee sudah punya agenda lain"),
    ("CF-05", "Masa libur semester", "Tidak ada kegiatan akademik"),
    ("CF-06", "Setelah pukul 18.00", "Terlalu malam untuk koordinasi"),
]

SMART_TASK_ROLES = {"GURU", "WALI_KELAS", "KEPALA_MADRASAH", "OPERATOR"}


def _task_to_dict(task) -> dict:
    return {k: v for k, v in asdict(task).items()}


def _short_deadline(value: str) -> str:
    """Ubah ISO datetime menjadi bentuk ringkas yang aman untuk kolom tabel."""
    if not value:
        return "-"
    text = str(value)
    if "T" in text:
        date_part, _, rest = text.partition("T")
        hhmm = rest[:5]
        try:
            y, m, d = date_part.split("-")
            return f"{d}/{m} {hhmm}"
        except ValueError:
            return text[:16]
    return text


def _print_tasks(tasks: list) -> None:
    if not tasks:
        print("(tidak ada tugas terdeteksi)")
        return
    header = f"{'ID':<8} {'AKSI':<19} {'OBJEK':<32} {'PIC':<12} {'TENGGAT':<11} PRIORITAS"
    print(header)
    print("-" * len(header))
    for t in tasks:
        obj = t.object if len(t.object) <= 31 else t.object[:30].rstrip() + "…"
        pic = t.assignee or "-"
        deadline = _short_deadline(t.deadline or t.deadline_text)
        flag = f"  ⚠️ {t.conflict_code}" if getattr(t, "conflict_code", None) else ""
        print(f"{t.task_id:<8} {t.action:<19} {obj:<32} {pic:<12} {deadline:<11} "
              f"{t.priority}{flag}")


def cmd_decompose(args: argparse.Namespace) -> int:
    tasks = decompose(args.input, NOW)
    print(f"📋 {len(tasks)} tugas terdeteksi dari input:\n   \"{args.input}\"\n")
    _print_tasks(tasks)
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps([_task_to_dict(t) for t in tasks], ensure_ascii=False, indent=2),
            encoding="utf-8")
        print(f"\n💾 Disimpan ke {args.json_out}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    if not args.input:
        print("❌ Sertakan --input \"<teks tugas>\" untuk divalidasi.", file=sys.stderr)
        return 2
    tasks = decompose(args.input, NOW)
    validated = validate(tasks, NOW)

    conflicts = [t for t in validated if getattr(t, "conflict_code", None)]
    print(f"🔍 Validasi {len(validated)} tugas — {len(conflicts)} konflik terdeteksi\n")
    _print_tasks(validated)

    if conflicts:
        print("\n⚠️  Detail konflik:")
        for t in conflicts:
            print(f"   [{t.conflict_code}] {t.task_id}: {t.conflict}")
            if t.suggestion:
                print(f"        → usulan: {t.suggestion}")
    else:
        print("\n✅ Tidak ada konflik jadwal.")
    return 0


def cmd_screen(args: argparse.Namespace) -> int:
    tasks = decompose(args.input, NOW)
    if not tasks:
        print("❌ Informasi tidak lengkap. Mohon sebutkan: (1) Hari/tanggal, "
              "(2) Jam, (3) Agenda, (4) Siapa yang hadir.")
        return 1
    tasks = validate(tasks, NOW)
    questions = clarify(tasks)
    print(confirmation_screen(tasks, questions))
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    tasks = decompose(args.input or "", NOW)
    if not tasks:
        print("❌ Tidak ada tugas untuk diproses. Sertakan --input.", file=sys.stderr)
        return 2
    tasks = validate(tasks, NOW)
    session = ApprovalSession(tasks=tasks)

    role = args.by.upper()
    if role not in SMART_TASK_ROLES:
        print(f"❌ Akses ditolak. Role {role} tidak boleh menjalankan Smart Task Handler.")
        return 1

    decision = args.decision.lower()
    if decision in {"approve", "setujui"}:
        result = approve(session, role)
        print(f"✅ State: {result['state']} (disetujui oleh {role})\n")
        for t in result.get("tasks", []):
            from asisten_madrasah import mock_execute
            print(f"   {mock_execute(t)}")
    elif decision in {"reject", "tolak"}:
        for _ in range(args.times):
            result = reject(session, role)
        print(f"{result.get('message', '')}\n   State: {result['state']}")
    else:
        print(f"❌ Keputusan tidak dikenal: {args.decision}", file=sys.stderr)
        return 2

    print("\n📜 Riwayat:", " → ".join(session.history))
    return 0


def cmd_conflicts(_: argparse.Namespace) -> int:
    print("Kode konflik yang dideteksi Smart Task Handler:\n")
    print(f"{'KODE':<8} {'KONDISI':<38} PENJELASAN")
    print("-" * 82)
    for code, condition, note in CONFLICT_CATALOG:
        print(f"{code:<8} {condition:<38} {note}")
    return 0


def cmd_demo(_: argparse.Namespace) -> int:
    user = User(id="u_kepala", name="Ahmad Fauzi", role="KEPALA_MADRASAH")
    message = ("Tolong kirim notulen rapat ke Pak Ahmad, jadwalkan follow-up "
               "Jumat siang jam 12.00, dan minta Pak Ahmad dan Bu Siti hadir "
               "rapat besok.")
    print(f"👤 {user.name} ({user.role})")
    print(f"💬 \"{message}\"\n")

    result = smart_task(user, message)
    if not result.get("ok"):
        print(f"❌ {result.get('message')}")
        return 1

    if result.get("injection_notice"):
        print(f"🛡️  {result['injection_notice']}\n")

    print(result["screen"])
    print("\n" + "=" * 70)
    session = result["session"]
    out = approve(session, user.role)
    print(f"✅ Disetujui → state {out['state']}\n")
    from asisten_madrasah import mock_execute
    for t in out.get("tasks", []):
        print(f"   {mock_execute(t)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Smart Task Handler CLI — Asisten Madrasah")
    sub = parser.add_subparsers(dest="command", required=True)

    p_dec = sub.add_parser("decompose", help="pecah pesan jadi tugas")
    p_dec.add_argument("--input", required=True)
    p_dec.add_argument("--json-out", default=None, help="simpan hasil ke file JSON")
    p_dec.set_defaults(func=cmd_decompose)

    p_val = sub.add_parser("validate", help="cek konflik CF-01..CF-06")
    p_val.add_argument("--input", required=True)
    p_val.add_argument("--file", default=None, help="(opsional) path tasks.json, dicatat saja)")
    p_val.set_defaults(func=cmd_validate)

    p_scr = sub.add_parser("screen", help="tampilkan layar konfirmasi")
    p_scr.add_argument("--input", required=True)
    p_scr.set_defaults(func=cmd_screen)

    p_app = sub.add_parser("approve", help="jalankan approval gate")
    p_app.add_argument("--input", default=None)
    p_app.add_argument("--file", default=None)
    p_app.add_argument("--decision", default="approve",
                       choices=["approve", "reject", "setujui", "tolak"])
    p_app.add_argument("--by", default="KEPALA_MADRASAH")
    p_app.add_argument("--times", type=int, default=1,
                       help="jumlah penolakan (untuk uji eskalasi 3x)")
    p_app.set_defaults(func=cmd_approve)

    p_cf = sub.add_parser("conflicts", help="daftar kode konflik")
    p_cf.set_defaults(func=cmd_conflicts)

    p_demo = sub.add_parser("demo", help="demo alur lengkap end-to-end")
    p_demo.set_defaults(func=cmd_demo)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
