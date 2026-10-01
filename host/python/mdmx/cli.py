"""Minimal real-hardware sender for MDMX.

Example:
    python -m mdmx.cli --device /dev/ttyACM0 --sequence 1 --fill 32
"""

from __future__ import annotations

import argparse

from .protocol import encode_frameset
from .transport import open_serial, send_frameset


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", required=True)
    parser.add_argument("--sequence", type=lambda x: int(x, 0), default=1)
    parser.add_argument("--fill", type=lambda x: int(x, 0), default=0)
    parser.add_argument("--timeout", type=float, default=0.250)
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()

    if not 0 <= args.fill <= 255:
        parser.error("--fill must be between 0 and 255")

    universes = [bytes([args.fill]) * 512 for _ in range(4)]
    frame = encode_frameset(args.sequence & 0xFFFFFFFF, universes)

    port = open_serial(args.device)
    try:
        result = send_frameset(
            port,
            frame,
            timeout=args.timeout,
            retries=args.retries,
        )
    finally:
        port.close()

    print(
        f"status=0x{result.reply.status:02X} "
        f"sequence={result.reply.sequence} "
        f"attempts={result.attempts}"
    )
    return 0 if result.reply.is_ack else 2


if __name__ == "__main__":
    raise SystemExit(main())
