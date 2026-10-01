import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from mdmx.protocol import (
    FRAME_LEN,
    HEADER_LEN,
    PAYLOAD_LEN,
    ProtocolError,
    STATUS_ACK,
    crc32_iso_hdlc,
    decode_frameset,
    decode_reply,
    encode_frameset,
    encode_reply,
    sequence_relation,
)


def universes():
    return [
        bytes([0x00]) * 512,
        bytes([0x55]) * 512,
        bytes([0xAA]) * 512,
        bytes(range(256)) * 2,
    ]


class ProtocolTests(unittest.TestCase):
    def test_canonical_size_and_header(self):
        frame = encode_frameset(1, universes())
        self.assertEqual(len(frame), FRAME_LEN)
        self.assertEqual(frame[:4], b"MDMX")
        self.assertEqual(frame[4], 1)
        self.assertEqual(frame[5], 1)
        self.assertEqual(int.from_bytes(frame[6:8], "little"), HEADER_LEN)
        self.assertEqual(int.from_bytes(frame[8:12], "little"), 1)
        self.assertEqual(int.from_bytes(frame[12:14], "little"), PAYLOAD_LEN)
        self.assertEqual(frame[14:16], b"\x00\x00")

    def test_round_trip(self):
        frame = encode_frameset(0x10203040, universes())
        decoded = decode_frameset(frame)
        self.assertEqual(decoded.sequence, 0x10203040)
        self.assertEqual(list(decoded.universes), universes())

    def test_crc_covers_header_and_payload(self):
        frame = encode_frameset(2, universes())
        stored = int.from_bytes(frame[-4:], "little")
        self.assertEqual(stored, crc32_iso_hdlc(frame[:-4]))

    def test_corruption_is_rejected(self):
        frame = bytearray(encode_frameset(2, universes()))
        frame[16] ^= 0x01
        with self.assertRaises(ProtocolError):
            decode_frameset(bytes(frame))

    def test_reply(self):
        raw = encode_reply(STATUS_ACK, 123)
        reply = decode_reply(raw)
        self.assertTrue(reply.is_ack)
        self.assertEqual(reply.sequence, 123)

    def test_sequence_duplicate(self):
        self.assertEqual(sequence_relation(9, 9), "duplicate")

    def test_sequence_new(self):
        self.assertEqual(sequence_relation(10, 9), "new")

    def test_sequence_stale(self):
        self.assertEqual(sequence_relation(8, 9), "stale")

    def test_sequence_wrap(self):
        self.assertEqual(sequence_relation(0, 0xFFFFFFFF), "new")


if __name__ == "__main__":
    unittest.main()
