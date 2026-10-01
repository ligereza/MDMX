"""Canonical MDMX FRAMESET_V1 wire codec.

Wire contract: docs/FRAMESET_V1.md
This module intentionally contains no fixture semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
import struct
import zlib

MAGIC = b"MDMX"
VERSION = 0x01
TYPE_FRAMESET = 0x01
HEADER_LEN = 16
PORTS = 4
SLOTS_PER_PORT = 512
PAYLOAD_LEN = PORTS * SLOTS_PER_PORT
FRAME_LEN = HEADER_LEN + PAYLOAD_LEN + 4
REPLY_LEN = 8

STATUS_ACK = 0x00
STATUS_ERR_CRC = 0x01
STATUS_ERR_FORMAT = 0x02
STATUS_ERR_SEQUENCE = 0x03

_HEADER = struct.Struct("<4sBBHIHH")
_REPLY = struct.Struct("<2sBBI")
_U32 = struct.Struct("<I")


class ProtocolError(ValueError):
    pass


@dataclass(frozen=True)
class FrameSet:
    sequence: int
    universes: tuple[bytes, bytes, bytes, bytes]
    flags: int = 0

    def encode(self) -> bytes:
        return encode_frameset(self.sequence, self.universes, self.flags)


@dataclass(frozen=True)
class Reply:
    status: int
    sequence: int

    @property
    def is_ack(self) -> bool:
        return self.status == STATUS_ACK


def crc32_iso_hdlc(data: bytes) -> int:
    """CRC-32/ISO-HDLC (aka IEEE CRC-32), returned as unsigned uint32."""
    return zlib.crc32(data) & 0xFFFFFFFF


def _coerce_universe(data: bytes | bytearray | memoryview) -> bytes:
    out = bytes(data)
    if len(out) != SLOTS_PER_PORT:
        raise ProtocolError(
            f"Each universe must contain exactly {SLOTS_PER_PORT} slots; got {len(out)}"
        )
    return out


def encode_frameset(
    sequence: int,
    universes: tuple[bytes, bytes, bytes, bytes] | list[bytes],
    flags: int = 0,
) -> bytes:
    if not 0 <= sequence <= 0xFFFFFFFF:
        raise ProtocolError("sequence must fit uint32")
    if not 0 <= flags <= 0xFFFF:
        raise ProtocolError("flags must fit uint16")
    if len(universes) != PORTS:
        raise ProtocolError(f"FRAMESET_V1 requires exactly {PORTS} universes")

    payload = b"".join(_coerce_universe(u) for u in universes)
    header = _HEADER.pack(
        MAGIC,
        VERSION,
        TYPE_FRAMESET,
        HEADER_LEN,
        sequence,
        PAYLOAD_LEN,
        flags,
    )
    body = header + payload
    crc = crc32_iso_hdlc(body)
    frame = body + _U32.pack(crc)
    assert len(frame) == FRAME_LEN
    return frame


def decode_frameset(frame: bytes) -> FrameSet:
    if len(frame) != FRAME_LEN:
        raise ProtocolError(f"FRAMESET_V1 must be {FRAME_LEN} bytes; got {len(frame)}")

    magic, version, msg_type, header_len, sequence, payload_len, flags = _HEADER.unpack_from(frame, 0)

    if magic != MAGIC:
        raise ProtocolError("bad magic")
    if version != VERSION:
        raise ProtocolError("unsupported version")
    if msg_type != TYPE_FRAMESET:
        raise ProtocolError("unsupported message type")
    if header_len != HEADER_LEN:
        raise ProtocolError("bad header_len")
    if payload_len != PAYLOAD_LEN:
        raise ProtocolError("bad payload_len")

    stored_crc = _U32.unpack_from(frame, FRAME_LEN - 4)[0]
    computed_crc = crc32_iso_hdlc(frame[:-4])
    if stored_crc != computed_crc:
        raise ProtocolError(
            f"CRC mismatch: stored=0x{stored_crc:08X}, computed=0x{computed_crc:08X}"
        )

    payload = frame[HEADER_LEN:-4]
    universes = tuple(
        payload[i * SLOTS_PER_PORT : (i + 1) * SLOTS_PER_PORT]
        for i in range(PORTS)
    )
    return FrameSet(sequence=sequence, universes=universes, flags=flags)  # type: ignore[arg-type]


def encode_reply(status: int, sequence: int) -> bytes:
    if not 0 <= status <= 0xFF:
        raise ProtocolError("status must fit uint8")
    if not 0 <= sequence <= 0xFFFFFFFF:
        raise ProtocolError("sequence must fit uint32")
    return _REPLY.pack(b"MR", VERSION, status, sequence)


def decode_reply(data: bytes) -> Reply:
    if len(data) != REPLY_LEN:
        raise ProtocolError(f"reply must be {REPLY_LEN} bytes; got {len(data)}")
    magic, version, status, sequence = _REPLY.unpack(data)
    if magic != b"MR":
        raise ProtocolError("bad reply magic")
    if version != VERSION:
        raise ProtocolError("unsupported reply version")
    return Reply(status=status, sequence=sequence)


def sequence_relation(candidate: int, last_committed: int) -> str:
    """Return 'duplicate', 'new', or 'stale' using uint32 modular ordering."""
    candidate &= 0xFFFFFFFF
    last_committed &= 0xFFFFFFFF
    delta = (candidate - last_committed) & 0xFFFFFFFF
    if delta == 0:
        return "duplicate"
    if delta < 0x80000000:
        return "new"
    return "stale"
