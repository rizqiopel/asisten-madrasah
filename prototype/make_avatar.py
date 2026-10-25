"""Generate a valid 512x512 PNG avatar without external dependencies."""
import struct
import zlib
from pathlib import Path

W = H = 512

TEAL = (13, 148, 136)
TEAL_DARK = (15, 118, 110)
GOLD = (245, 158, 11)
WHITE = (255, 255, 255)

rows = []
cx, cy = W / 2, H / 2

for y in range(H):
    row = bytearray()
    row.append(0)  # filter type 0
    for x in range(W):
        dx, dy = x - cx, y - cy
        dist = (dx * dx + dy * dy) ** 0.5

        # Lingkaran luar (avatar background)
        if dist < 240:
            color = TEAL
        else:
            color = WHITE

        # Cincin emas
        if 200 <= dist < 240:
            color = GOLD

        # Kepala (bulatan atas)
        hx, hy = x - cx, y - 170
        if (hx * hx) / (58 * 58) + (hy * hy) / (62 * 62) <= 1:
            color = WHITE

        # Bahu / tubuh (setengah elips bawah)
        bx, by = x - cx, y - 400
        if (bx * bx) / (130 * 130) + (by * by) / (150 * 150) <= 1 and y >= 300:
            color = WHITE

        row.extend(color)
    rows.append(bytes(row))

raw = b"".join(rows)


def chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)  # 8-bit RGB
png = (
    b"\x89PNG\r\n\x1a\n"
    + chunk(b"IHDR", ihdr)
    + chunk(b"IDAT", zlib.compress(raw, 9))
    + chunk(b"IEND", b"")
)

out = Path(__file__).resolve().parent.parent / "expert-package" / "avatars" / "asisten-madrasah.png"
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "wb") as f:
    f.write(png)

print(f"Avatar dibuat: {out}")
print(f"Ukuran: {len(png)} bytes ({W}x{H} RGB)")
