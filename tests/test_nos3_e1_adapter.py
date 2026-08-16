import hashlib
import unittest

from src.mission_recovery.events import materialize_event
from src.mission_recovery.nos3_e1_adapter import (
    build_sample_noop_packet,
    build_sample_reset_counters_packet,
    send_e1_once,
)


class FakeSocket:
    def __init__(self):
        self.calls = []

    def sendto(self, payload, target):
        self.calls.append((payload, target))
        return len(payload)


def e1_event():
    return materialize_event(
        "E1",
        mission_state="M0",
        contact_condition="C0",
        evidence_condition="T0",
        seed=1,
    )


class Nos3E1AdapterTests(unittest.TestCase):
    def test_noop_packet_matches_pinned_sample_definition(self):
        packet = build_sample_noop_packet()
        self.assertEqual(packet.hex(), "18fac000000100dc")
        self.assertEqual(
            hashlib.sha256(packet).hexdigest(),
            "722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd",
        )

    def test_reset_packet_matches_r015_surrogate(self):
        packet = build_sample_reset_counters_packet()
        self.assertEqual(packet.hex(), "18fac000000101dd")
        self.assertEqual(
            hashlib.sha256(packet).hexdigest(),
            "c8a8692bad90aab74ffe550c87e93ed83838d4b4f45c57a609a00455292d41cb",
        )

    def test_packet_checksums_are_valid(self):
        for packet in (
            build_sample_noop_packet(),
            build_sample_reset_counters_packet(),
        ):
            value = 0
            for byte in packet:
                value ^= byte
            self.assertEqual(value, 0xFF)

    def test_default_send_is_exactly_one_noop_datagram(self):
        sock = FakeSocket()
        result = send_e1_once(e1_event(), sock=sock)
        self.assertEqual(len(sock.calls), 1)
        self.assertEqual(result["datagrams_sent"], 1)
        self.assertEqual(result["command_class"], "sample_noop")
        self.assertEqual(sock.calls[0][1], ("nos-fsw", 5012))

    def test_reset_send_is_exactly_one_internal_datagram(self):
        sock = FakeSocket()
        result = send_e1_once(
            e1_event(),
            command_class="sample_reset_counters",
            sock=sock,
        )
        self.assertEqual(len(sock.calls), 1)
        self.assertEqual(result["datagrams_sent"], 1)
        self.assertEqual(
            result["command_class"],
            "sample_reset_counters",
        )
        self.assertEqual(
            result["packet_sha256"],
            "c8a8692bad90aab74ffe550c87e93ed83838d4b4f45c57a609a00455292d41cb",
        )
        self.assertEqual(sock.calls[0][1], ("nos-fsw", 5012))

    def test_non_e1_event_rejected(self):
        event = materialize_event(
            "E2",
            mission_state="M0",
            contact_condition="C0",
            evidence_condition="T0",
            seed=1,
        )
        with self.assertRaises(ValueError):
            send_e1_once(event, sock=FakeSocket())

    def test_external_target_rejected(self):
        with self.assertRaises(ValueError):
            send_e1_once(
                e1_event(),
                host="example.com",
                sock=FakeSocket(),
            )


if __name__ == "__main__":
    unittest.main()
