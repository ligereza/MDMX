"""USB CDC stop-and-wait transport for MDMX.

Requires pyserial only when talking to real hardware.
"""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Protocol

from .protocol import FRAME_LEN, REPLY_LEN, Reply, decode_reply


class SerialLike(Protocol):
    timeout: float | None

    def write(self, data: bytes) -> int: ...
    def read(self, size: int) -> bytes: ...
    def reset_input_buffer(self) -> None: ...


class TransportError(RuntimeError):
    pass


@dataclass
class SendResult:
    reply: Reply
    attempts: int


def _write_all(port: SerialLike, data: bytes, deadline: float) -> None:
    view = memoryview(data)
    offset = 0
    while offset < len(view):
        if time.monotonic() >= deadline:
            raise TimeoutError("timeout while writing FRAMESET_V1")
        written = port.write(view[offset:])
        if written is None:
            written = 0
        if written < 0:
            raise TransportError("serial write returned a negative byte count")
        if written == 0:
            time.sleep(0.001)
            continue
        offset += written


def _read_exact(port: SerialLike, size: int, deadline: float) -> bytes:
    out = bytearray()
    while len(out) < size:
        if time.monotonic() >= deadline:
            raise TimeoutError("timeout while waiting for MDMX reply")
        chunk = port.read(size - len(out))
        if chunk:
            out.extend(chunk)
        else:
            time.sleep(0.001)
    return bytes(out)


def send_frameset(
    port: SerialLike,
    frame: bytes,
    *,
    timeout: float = 0.250,
    retries: int = 2,
) -> SendResult:
    """Send the exact same frame on every retry.

    This preserves FRAMESET_V1 idempotency: same payload, same sequence, same CRC.
    """
    if len(frame) != FRAME_LEN:
        raise TransportError(f"refusing to send non-canonical frame length {len(frame)}")
    if retries < 0:
        raise ValueError("retries cannot be negative")

    expected_sequence = int.from_bytes(frame[8:12], "little")

    last_error: Exception | None = None
    for attempt in range(1, retries + 2):
        deadline = time.monotonic() + timeout
        try:
            if attempt == 1:
                port.reset_input_buffer()
            _write_all(port, frame, deadline)
            raw_reply = _read_exact(port, REPLY_LEN, deadline)
            reply = decode_reply(raw_reply)
            if reply.sequence != expected_sequence:
                raise TransportError(
                    f"reply sequence {reply.sequence} != sent sequence {expected_sequence}"
                )
            return SendResult(reply=reply, attempts=attempt)
        except (TimeoutError, TransportError, ValueError) as exc:
            last_error = exc

    raise TransportError(f"FRAMESET_V1 failed after {retries + 1} attempts: {last_error}")


def open_serial(device: str, *, timeout: float = 0.050):
    try:
        import serial  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install pyserial to use real hardware: pip install pyserial") from exc

    return serial.Serial(
        port=device,
        baudrate=115200,  # USB CDC ignores line baud on typical RP2040 stacks.
        timeout=timeout,
        write_timeout=timeout,
    )
