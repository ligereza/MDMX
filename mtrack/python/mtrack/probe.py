from __future__ import annotations

from dataclasses import dataclass
import json
import shutil
import subprocess

from .camera_config import ConfiguredCamera


@dataclass(frozen=True)
class StreamProbe:
    source_id: str
    codec: str
    width: int
    height: int
    frame_rate: str


def probe_camera(camera: ConfiguredCamera, *, timeout_s: float = 8.0) -> StreamProbe:
    """Probe one RTSP stream without recording it."""
    ffprobe = shutil.which("ffprobe")
    if ffprobe is None:
        raise RuntimeError("ffprobe is required but was not found in PATH")

    uri = camera.camera.rtsp_uri(
        camera.credentials.username,
        camera.credentials.password,
    )
    cmd = [
        ffprobe,
        "-v", "error",
        "-rtsp_transport", camera.camera.transport,
        "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,width,height,r_frame_rate",
        "-of", "json",
        uri,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=True,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"{camera.camera.source.source_id}: RTSP probe timed out"
        ) from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip().splitlines()
        safe_detail = detail[-1] if detail else "ffprobe failed"
        raise RuntimeError(
            f"{camera.camera.source.source_id}: RTSP probe failed: {safe_detail}"
        ) from None

    payload = json.loads(result.stdout)
    streams = payload.get("streams", [])
    if not streams:
        raise RuntimeError(
            f"{camera.camera.source.source_id}: no video stream returned"
        )
    stream = streams[0]
    return StreamProbe(
        source_id=camera.camera.source.source_id,
        codec=str(stream.get("codec_name", "unknown")),
        width=int(stream.get("width", 0)),
        height=int(stream.get("height", 0)),
        frame_rate=str(stream.get("r_frame_rate", "unknown")),
    )
