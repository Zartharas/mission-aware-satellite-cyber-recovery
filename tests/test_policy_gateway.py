import unittest

from src.mission_recovery.nos3_e1_adapter import build_sample_noop_packet
from src.mission_recovery.policy_gateway import (
    build_e1_envelope,
    decide_forward,
)


class PolicyGatewayTests(unittest.TestCase):
    def test_e1_envelope_uses_validated_packet(self):
        envelope = build_e1_envelope("modeled_attacker")
        self.assertEqual(envelope["packet_hex"], build_sample_noop_packet().hex())
        self.assertEqual(
            envelope["packet_sha256"],
            "722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd",
        )

    def test_p0_forwards_both_sources(self):
        self.assertTrue(
            decide_forward(
                "OBSERVE_ONLY",
                build_e1_envelope("modeled_attacker"),
            )
        )
        self.assertTrue(
            decide_forward(
                "OBSERVE_ONLY",
                build_e1_envelope("authorized_ground"),
            )
        )

    def test_p1_blocks_only_modeled_attacker(self):
        self.assertFalse(
            decide_forward(
                "ISOLATE_MODELED_SOURCE",
                build_e1_envelope("modeled_attacker"),
            )
        )
        self.assertTrue(
            decide_forward(
                "ISOLATE_MODELED_SOURCE",
                build_e1_envelope("authorized_ground"),
            )
        )

    def test_unsupported_action_rejected(self):
        with self.assertRaises(ValueError):
            decide_forward(
                "ENTER_SAFE_MODE",
                build_e1_envelope("modeled_attacker"),
            )


if __name__ == "__main__":
    unittest.main()
