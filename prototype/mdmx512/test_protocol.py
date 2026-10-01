import unittest

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


if __name__ == "__main__":
    unittest.main()
