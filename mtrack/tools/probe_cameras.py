#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from mtrack.camera_config import load_hikvision_config
from mtrack.probe import probe_camera


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Probe configured MTRACK cameras without recording video."
    )
    parser.add_argument("config", help="Path to camera TOML")
    args = parser.parse_args()

    cameras = load_hikvision_config(args.config)
    if not cameras:
        print("No cameras configured.")
        return 2

    failed = False
    for configured in cameras:
        source_id = configured.camera.source.source_id
        print(
            f"{source_id}: probing "
            f"{configured.camera.redacted_rtsp_uri(configured.credentials.username)}"
        )
        try:
            info = probe_camera(configured)
        except Exception as exc:
            failed = True
            print(f"{source_id}: FAIL: {exc}")
            continue
        print(
            f"{source_id}: OK codec={info.codec} "
            f"{info.width}x{info.height} fps={info.frame_rate}"
        )

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
