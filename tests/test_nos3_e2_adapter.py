import hashlib
import unittest

from src.mission_recovery.events import materialize_event
from src.mission_recovery.nos3_e1_adapter import build_sample_noop_packet
from src.mission_recovery.nos3_e2_adapter import send_replay_once


class FakeSocket:
    def __init__(self):
        self.calls = []

    def sendto(self, payload, target):
        self.calls.append((payload, target))
        return len(payload)


class Nos3E2AdapterTests(unittest.TestCase):
    def test_replay_packet_is_same_pinned_sample_noop(self):
        packet = build_sample_noop_packet()
        self.assertEqual(packet.hex(), "18fac000000100dc")
        self.assertEqual(
            hashlib.sha256(packet).hexdigest(),
            "722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd",
        )

    def test_e2_sends_exactly_one_replay_datagram(self):
        event = materialize_event(
            "E2",
            mission_state="M0",
            contact_condition="C0",
            evidence_condition="T0",
            seed=1,
        )
        sock = FakeSocket()
        result = send_replay_once(event, sock=sock)
        self.assertEqual(len(sock.calls), 1)
        self.assertEqual(result["datagrams_sent"], 1)
        self.assertEqual(result["role"], "replay_event")
        self.assertEqual(sock.calls[0][1], ("nos-fsw", 5012))

    def test_non_e2_event_rejected(self):
        event = materialize_event(
            "E1",
            mission_state="M0",
            contact_condition="C0",
            evidence_condition="T0",
            seed=1,
        )
        with self.assertRaises(ValueError):
            send_replay_once(event, sock=FakeSocket())

    def test_external_target_rejected(self):
        event = materialize_event(
            "E2",
            mission_state="M0",
            contact_condition="C0",
            evidence_condition="T0",
            seed=1,
        )
        with self.assertRaises(ValueError):
            send_replay_once(event, host="example.com", sock=FakeSocket())


if __name__ == "__main__":
    unittest.main()
