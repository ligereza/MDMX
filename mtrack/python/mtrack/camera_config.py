from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import tomllib

from .hikvision import HikvisionCamera
from .sources import ObservationSource, PrivacyPolicy, SourceKind


@dataclass(frozen=True)
class CameraCredentials:
    username: str
    password: str


@dataclass(frozen=True)
class ConfiguredCamera:
    camera: HikvisionCamera
    credentials: CameraCredentials


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


def load_hikvision_config(path: str | Path) -> tuple[ConfiguredCamera, ...]:
    """Load topology from TOML while sourcing secrets from env vars."""
    with open(path, "rb") as fh:
        data = tomllib.load(fh)

    cameras = []
    for item in data.get("camera", []):
        prefix = item["credential_env_prefix"]
        source = ObservationSource(
            source_id=item["id"],
            kind=SourceKind.ONVIF,
            host=item["host"],
            camera_role=item.get("camera_role", "fixed"),
            stream_role=item.get("stream_role", "analysis"),
            privacy=PrivacyPolicy(
                persist_video=False,
                persist_frames=False,
                biometric_identification=False,
                retain_derived_observations=item.get(
                    "retain_derived_observations", True
                ),
                max_frame_age_ms=item.get("max_frame_age_ms", 500),
            ),
        )
        camera = HikvisionCamera(
            source=source,
            channel=item.get("channel", 1),
            stream=item.get("stream", "sub"),
            rtsp_port=item.get("rtsp_port", 554),
            onvif_port=item.get("onvif_port", 80),
            transport=item.get("transport", "tcp"),
        )
        credentials = CameraCredentials(
            username=_required_env(f"{prefix}_USER"),
            password=_required_env(f"{prefix}_PASS"),
        )
        cameras.append(ConfiguredCamera(camera, credentials))

    return tuple(cameras)
