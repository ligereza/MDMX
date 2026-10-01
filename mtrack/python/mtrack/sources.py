from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping


class SourceKind(str, Enum):
    CCTV_RTSP = "cctv_rtsp"
    ONVIF = "onvif"
    MDMX_CAMERA = "mdmx_camera"
    SIMULATOR = "simulator"
    EXTERNAL_METADATA = "external_metadata"


@dataclass(frozen=True)
class PrivacyPolicy:
    """Runtime privacy contract for an observation source."""

    persist_video: bool = False
    persist_frames: bool = False
    biometric_identification: bool = False
    retain_derived_observations: bool = True
    max_frame_age_ms: int = 500

    def __post_init__(self) -> None:
        if self.max_frame_age_ms <= 0:
            raise ValueError("max_frame_age_ms must be positive")


@dataclass(frozen=True)
class ObservationSource:
    source_id: str
    kind: SourceKind
    host: str
    enabled: bool = True
    camera_role: str = "fixed"
    stream_role: str = "analysis"
    metadata: Mapping[str, str] = field(default_factory=dict)
    privacy: PrivacyPolicy = field(default_factory=PrivacyPolicy)

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("source_id cannot be empty")
        if not self.host.strip():
            raise ValueError("host cannot be empty")
