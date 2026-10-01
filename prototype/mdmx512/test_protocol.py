import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

from protocol import (
    Attribute,
    ChannelDef,
    Fixture,
    Lane,
    Opcode,
    Rig,
    decode_frame,
    encode_frame,
    expand,
)


ROOT = Path(__file__).resolve().parents[2]


def ten_fixture_rig() -> Rig:
    fixtures = {}
    ids = []
    for i in range(10):
        fixture_id = i + 1
        ids.append(fixture_id)
        fixtures[fixture_id] = Fixture(
            fixture_id=fixture_id,
            universe=1,
            address=1 + i * 51,
            footprint=51,
            channels={Attribute.DIMMER: ChannelDef(offset=0, bits=8)},
        )
    return Rig(fixtures=fixtures, groups={1: tuple(ids)})


def two_universe_rig() -> Rig:
    fixtures = {}
    ids = []
    for i in range(12):
        fixture_id = i + 1
        ids.append(fixture_id)
        universe = 1 if i < 6 else 2
        local = i if i < 6 else i - 6
        fixtures[fixture_id] = Fixture(
            fixture_id=fixture_id,
            universe=universe,
            address=1 + local * 51,
            footprint=51,
            channels={Attribute.DIMMER: ChannelDef(offset=0, bits=8)},
        )
    return Rig(fixtures=fixtures, groups={7: tuple(ids)})


class MDMX512Tests(unittest.TestCase):
    def test_512_byte_frame_round_trip(self):
        lane = Lane(
            enabled=True,
            opcode=Opcode.RAMP,
            attribute=Attribute.DIMMER,
            flags=0,
            target_group=1,
            p0=0,
            p1=65535,
        )
        raw = encode_frame([lane])
        self.assertEqual(len(raw), 512)

        decoded = decode_frame(raw)
        self.assertTrue(decoded.armed)
        self.assertEqual(decoded.lanes[0], lane)

    def test_one_lane_expands_to_ten_independent_dimmers(self):
        lane = Lane(
            enabled=True,
            opcode=Opcode.RAMP,
            attribute=Attribute.DIMMER,
            flags=0,
            target_group=1,
            p0=0,
            p1=65535,
        )
        output = expand(decode_frame(encode_frame([lane])), ten_fixture_rig())
        universe = output[1]

        slots = [universe[i * 51] for i in range(10)]
        self.assertEqual(slots, [0, 28, 57, 85, 113, 142, 170, 198, 227, 255])

    def test_one_lane_can_span_multiple_output_universes(self):
        lane = Lane(
            enabled=True,
            opcode=Opcode.RAMP,
            attribute=Attribute.DIMMER,
            flags=0,
            target_group=7,
            p0=0,
            p1=65535,
        )
        output = expand(decode_frame(encode_frame([lane])), two_universe_rig())
        self.assertEqual(set(output), {1, 2})
        values = [output[1][i * 51] for i in range(6)] + [output[2][i * 51] for i in range(6)]
        self.assertEqual(values[0], 0)
        self.assertEqual(values[-1], 255)
        self.assertTrue(all(a <= b for a, b in zip(values, values[1:])))

    def test_global_master_scales_derived_dimmer(self):
        lane = Lane(
            enabled=True,
            opcode=Opcode.SET,
            attribute=Attribute.DIMMER,
            flags=0,
            target_group=1,
            p0=65535,
        )
        frame = decode_frame(encode_frame([lane], global_master=32768))
        output = expand(frame, ten_fixture_rig())
        self.assertTrue(all(output[1][i * 51] in (127, 128) for i in range(10)))

    def test_avolites_personality_is_well_formed_and_has_expected_modes(self):
        path = ROOT / "fixtures" / "avolites" / "MDMX_MDMX512_EXPERIMENTAL.d4"
        root = ET.parse(path).getroot()
        self.assertEqual(root.attrib["Name"], "MDMX512")

        modes = {m.attrib["Name"]: m for m in root.findall("Mode")}
        self.assertIn("64 DMX (3 lanes)", modes)
        self.assertIn("128 DMX (7 lanes)", modes)
        self.assertIn("256 DMX (15 lanes)", modes)
        self.assertIn("512 DMX (31 lanes)", modes)
        self.assertIn("Lane", modes)

        cells = modes["512 DMX (31 lanes)"].find("Cells").findall("Cell")
        self.assertEqual(len(cells), 31)
        self.assertEqual(cells[0].attrib["ChannelOffset"], "17")
        self.assertEqual(cells[-1].attrib["ChannelOffset"], "497")


if __name__ == "__main__":
    unittest.main()
