"""Experimental MDMX512 control-plane prototype.

A 512-slot DMX universe is treated as a declarative control frame, not as
512 physical output channels.

Layout:
  16-byte global header
  31 x 16-byte operator lanes = 496 bytes
Total: 512 bytes

16-bit values use DMX convention: coarse byte first, fine byte second.
This is experimental and intentionally separate from frozen FRAMESET_V1.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
import math

FRAME_SIZE = 512
HEADER_SIZE = 16
LANE_SIZE = 16
LANE_COUNT = 31
MAGIC = b"MDMX"
VERSION = 1
PROFILE = 1

FLAG_ARMED = 0x01
LANE_REVERSE = 0x01


class Opcode(IntEnum):
    OFF = 0
    SET = 1
    RAMP = 2
    WAVE = 3


class Attribute(IntEnum):
    NONE = 0
    DIMMER = 1
    PAN = 2
    TILT = 3
    RED = 4
    GREEN = 5
    BLUE = 6
    WHITE = 7
    ZOOM = 8


@dataclass(frozen=True)
class Lane:
    enabled: bool
    opcode: Opcode
    attribute: Attribute
    flags: int
    target_group: int
    p0: int = 0
    p1: int = 0
    p2: int = 0
    p3: int = 0
    p4: int = 0


@dataclass(frozen=True)
class ControlFrame:
    armed: bool
    bank: int
    global_master: int
    lanes: tuple[Lane, ...]


@dataclass(frozen=True)
class ChannelDef:
    offset: int
    bits: int = 8


@dataclass(frozen=True)
class Fixture:
    fixture_id: int
    universe: int
    address: int
    footprint: int
    channels: dict[Attribute, ChannelDef]


@dataclass(frozen=True)
class Rig:
    fixtures: dict[int, Fixture]
    groups: dict[int, tuple[int, ...]]


class ProtocolError(ValueError):
    pass


def u16be(data: bytes | bytearray, offset: int) -> int:
    return (data[offset] << 8) | data[offset + 1]


def put_u16be(data: bytearray, offset: int, value: int) -> None:
    value = max(0, min(0xFFFF, int(value)))
    data[offset] = (value >> 8) & 0xFF
    data[offset + 1] = value & 0xFF


def encode_lane(lane: Lane) -> bytes:
    out = bytearray(LANE_SIZE)
    out[0] = 255 if lane.enabled else 0
    out[1] = int(lane.opcode)
    out[2] = int(lane.attribute)
    out[3] = lane.flags & 0xFF
    put_u16be(out, 4, lane.target_group)
    for offset, value in zip(
        (6, 8, 10, 12, 14),
        (lane.p0, lane.p1, lane.p2, lane.p3, lane.p4),
    ):
        put_u16be(out, offset, value)
    return bytes(out)


def decode_lane(data: bytes | bytearray) -> Lane:
    if len(data) != LANE_SIZE:
        raise ProtocolError("lane must be exactly 16 bytes")
    try:
        opcode = Opcode(data[1])
        attribute = Attribute(data[2])
    except ValueError as exc:
        raise ProtocolError(str(exc)) from exc

    return Lane(
        enabled=data[0] >= 128,
        opcode=opcode,
        attribute=attribute,
        flags=data[3],
        target_group=u16be(data, 4),
        p0=u16be(data, 6),
        p1=u16be(data, 8),
        p2=u16be(data, 10),
        p3=u16be(data, 12),
        p4=u16be(data, 14),
    )


def encode_frame(
    lanes: list[Lane] | tuple[Lane, ...],
    *,
    armed: bool = True,
    bank: int = 0,
    global_master: int = 0xFFFF,
) -> bytes:
    if len(lanes) > LANE_COUNT:
        raise ProtocolError(f"maximum {LANE_COUNT} lanes")

    out = bytearray(FRAME_SIZE)
    out[0:4] = MAGIC
    out[4] = VERSION
    out[5] = PROFILE
    out[6] = FLAG_ARMED if armed else 0
    out[7] = bank & 0xFF
    put_u16be(out, 8, global_master)

    for index, lane in enumerate(lanes):
        start = HEADER_SIZE + index * LANE_SIZE
        out[start:start + LANE_SIZE] = encode_lane(lane)

    return bytes(out)


def decode_frame(data: bytes | bytearray) -> ControlFrame:
    if len(data) != FRAME_SIZE:
        raise ProtocolError("MDMX512 requires exactly 512 slots")
    if bytes(data[0:4]) != MAGIC:
        raise ProtocolError("bad MDMX512 magic")
    if data[4] != VERSION or data[5] != PROFILE:
        raise ProtocolError("unsupported MDMX512 version/profile")

    lanes = []
    for index in range(LANE_COUNT):
        start = HEADER_SIZE + index * LANE_SIZE
        lane = decode_lane(data[start:start + LANE_SIZE])
        lanes.append(lane)

    return ControlFrame(
        armed=bool(data[6] & FLAG_ARMED),
        bank=data[7],
        global_master=u16be(data, 8),
        lanes=tuple(lanes),
    )


def _lerp_u16(a: int, b: int, i: int, n: int) -> int:
    if n <= 1:
        return a
    numerator = (b - a) * i
    if numerator >= 0:
        delta = (numerator + (n - 1) // 2) // (n - 1)
    else:
        delta = -((-numerator + (n - 1) // 2) // (n - 1))
    return max(0, min(0xFFFF, a + delta))


def _u16_to_u8(value: int) -> int:
    return (max(0, min(0xFFFF, value)) * 255 + 32767) // 65535


def _wave_u16(center: int, amplitude: int, phase_u16: int) -> int:
    center_norm = center / 65535.0
    amp_norm = amplitude / 65535.0
    phase = (phase_u16 / 65535.0) * math.tau
    value = center_norm + math.sin(phase) * amp_norm
    return max(0, min(0xFFFF, int(round(value * 65535.0))))


def _write_attribute(
    universes: dict[int, bytearray],
    fixture: Fixture,
    attribute: Attribute,
    value_u16: int,
) -> None:
    channel = fixture.channels.get(attribute)
    if channel is None:
        return

    if fixture.address < 1 or fixture.address + fixture.footprint - 1 > 512:
        raise ProtocolError(f"fixture {fixture.fixture_id} has invalid patch")

    slot = fixture.address - 1 + channel.offset
    universe = universes.setdefault(fixture.universe, bytearray(512))

    if channel.bits == 8:
        universe[slot] = _u16_to_u8(value_u16)
    elif channel.bits == 16:
        if slot + 1 >= 512:
            raise ProtocolError("16-bit attribute crosses universe boundary")
        universe[slot] = (value_u16 >> 8) & 0xFF
        universe[slot + 1] = value_u16 & 0xFF
    else:
        raise ProtocolError(f"unsupported channel width: {channel.bits}")


def expand(frame: ControlFrame, rig: Rig, *, time_phase_u16: int = 0) -> dict[int, bytes]:
    """Expand one MDMX512 snapshot into any number of physical universes."""
    universes: dict[int, bytearray] = {}
    if not frame.armed:
        return {}

    for lane in frame.lanes:
        if not lane.enabled or lane.opcode == Opcode.OFF:
            continue

        fixture_ids = rig.groups.get(lane.target_group, ())
        if lane.flags & LANE_REVERSE:
            fixture_ids = tuple(reversed(fixture_ids))
        n = len(fixture_ids)

        for i, fixture_id in enumerate(fixture_ids):
            fixture = rig.fixtures[fixture_id]

            if lane.opcode == Opcode.SET:
                value = lane.p0
            elif lane.opcode == Opcode.RAMP:
                value = _lerp_u16(lane.p0, lane.p1, i, n)
            elif lane.opcode == Opcode.WAVE:
                spread = _lerp_u16(0, lane.p3, i, n)
                phase = (time_phase_u16 + lane.p4 + spread) & 0xFFFF
                value = _wave_u16(lane.p0, lane.p1, phase)
            else:
                continue

            if lane.attribute == Attribute.DIMMER:
                value = (value * frame.global_master + 32767) // 65535

            _write_attribute(universes, fixture, lane.attribute, value)

    return {universe: bytes(data) for universe, data in universes.items()}
