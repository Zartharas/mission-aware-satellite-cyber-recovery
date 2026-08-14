import unittest

from src.mission_recovery.nos3_e4_adapter import (
    build_enable_output_packet,
    build_send_data_types_packet,
    build_send_housekeeping_packet,
    send_once,
)
from src.mission_recovery.telemetry_visibility import (
    HIGH_VALUE_MID,
    packet_mid,
    should_forward,
)


class FakeSocket:
    def __init__(self):
        self.calls = []

    def sendto(self, payload, target):
        self.calls.append((payload, target))
        return len(payload)


class E4AdapterTests(unittest.TestCase):
    def test_send_data_types_packet_identity(self):
        packet = build_send_data_types_packet()
        self.assertEqual(packet.hex(), "18e8c000000103cd")
        self.assertEqual(len(packet), 8)
        value = 0
        for byte in packet:
            value ^= byte
        self.assertEqual(value, 0xFF)

    def test_send_housekeeping_packet_identity(self):
        packet = build_send_housekeeping_packet()
        self.assertEqual(packet.hex(), "18e9c000000100cf")
        self.assertEqual(len(packet), 8)

    def test_enable_output_packet(self):
        packet = build_enable_output_packet("e4-proxy")
        self.assertEqual(
            packet.hex(),
            "18e8c000001102cc65342d70726f78790000000000000000",
        )
        self.assertEqual(len(packet), 24)

    def test_external_target_rejected(self):
        with self.assertRaises(ValueError):
            send_once(
                build_send_data_types_packet(),
                role="test",
                host="example.com",
                sock=FakeSocket(),
            )

    def test_data_types_mid_parser(self):
        self.assertEqual(packet_mid(bytes.fromhex("08e90000")), HIGH_VALUE_MID)

    def test_control_forwards_high_value(self):
        self.assertTrue(should_forward("control", HIGH_VALUE_MID))

    def test_degraded_suppresses_high_value_only(self):
        self.assertFalse(should_forward("degraded", HIGH_VALUE_MID))
        self.assertTrue(should_forward("degraded", 0x08E8))
        self.assertTrue(should_forward("control", HIGH_VALUE_MID))


if __name__ == "__main__":
    unittest.main()
