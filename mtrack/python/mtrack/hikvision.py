from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

from .sources import ObservationSource, SourceKind


_STREAM_SUFFIX = {
    "main": "01",
    "sub": "02",
}


@dataclass(frozen=True)
class HikvisionCamera:
    """Connection metadata for a Hikvision camera.

    Credentials are deliberately excluded so they can live in environment
    variables or a secret store rather than in the rig file.
    """

    source: ObservationSource
    channel: int = 1
    stream: str = "sub"
    rtsp_port: int = 554
    onvif_port: int = 80
    transport: str = "tcp"

    def __post_init__(self) -> None:
        if self.source.kind not in (SourceKind.CCTV_RTSP, SourceKind.ONVIF):
            raise ValueError("HikvisionCamera requires a CCTV/ONVIF source")
        if self.channel < 1:
            raise ValueError("channel must be >= 1")
        if self.stream not in _STREAM_SUFFIX:
            raise ValueError("stream must be 'main' or 'sub'")
        if not 1 <= self.rtsp_port <= 65535:
            raise ValueError("invalid RTSP port")
        if not 1 <= self.onvif_port <= 65535:
            raise ValueError("invalid ONVIF port")
        if self.transport not in ("tcp", "udp"):
            raise ValueError("transport must be tcp or udp")

    @property
    def rtsp_path(self) -> str:
        stream_number = f"{self.channel}{_STREAM_SUFFIX[self.stream]}"
        return f"/Streaming/Channels/{stream_number}"

    def rtsp_uri(self, username: str, password: str) -> str:
        if not username:
            raise ValueError("username cannot be empty")
        user = quote(username, safe="")
        secret = quote(password, safe="")
        return (
            f"rtsp://{user}:{secret}@{self.source.host}:"
            f"{self.rtsp_port}{self.rtsp_path}"
        )

    def redacted_rtsp_uri(self, username: str = "<user>") -> str:
        return (
            f"rtsp://{quote(username, safe='')}:***@{self.source.host}:"
            f"{self.rtsp_port}{self.rtsp_path}"
        )

    @property
    def onvif_device_service(self) -> str:
        return (
            f"http://{self.source.host}:{self.onvif_port}"
            "/onvif/device_service"
        )
