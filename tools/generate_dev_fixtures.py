#!/usr/bin/env python3
"""Generate DEVELOPMENT fixtures from the canonical FRAMESET_V1 codec.

These files are intentionally separate from fixtures/frozen: they are not claimed
to be the historical golden blobs unless their SHA-256 matches the frozen manifest.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "host" / "python"))

from mdmx.protocol import encode_frameset


def pattern(seed: int) -> bytes:
    return bytes(((i * (seed * 2 + 1) + seed * 29) & 0xFF) for i in range(512))


def main() -> None:
    out_dir = ROOT / "fixtures" / "development"
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {"kind": "development", "warning": "Not historical frozen fixtures", "files": []}

    for sequence in (1, 2, 3):
        universes = [pattern(sequence + p) for p in range(4)]
        blob = encode_frameset(sequence, universes)
        name = f"dev-golden-{sequence}.bin"
        (out_dir / name).write_bytes(blob)
        manifest["files"].append({
            "name": name,
            "sequence": sequence,
            "bytes": len(blob),
            "sha256": hashlib.sha256(blob).hexdigest(),
            "crc_le_hex": blob[-4:].hex(),
        })

    source = out_dir / "dev-golden-2.bin"
    corrupted = bytearray(source.read_bytes())
    corrupted[16] ^= 0x01
    corrupt_name = "dev-corrupt-out1-seq2.bin"
    (out_dir / corrupt_name).write_bytes(corrupted)
    manifest["files"].append({
        "name": corrupt_name,
        "derived_from": source.name,
        "mutation": "byte[16] ^= 0x01; stored CRC unchanged",
        "bytes": len(corrupted),
        "sha256": hashlib.sha256(corrupted).hexdigest(),
        "crc_le_hex": corrupted[-4:].hex(),
    })

    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(manifest['files'])} development fixtures to {out_dir}")


if __name__ == "__main__":
    main()
