import hashlib
import unittest

from src.mission_recovery.nos3_e1_adapter import build_sample_noop_packet
from src.mission_recovery.policy_gateway import (
    build_command_envelope,
    build_e1_envelope,
    build_sample_noargs_packet,
    decide_forward,
)


class PolicyGatewayTests(unittest.TestCase):
    def test_noop_packet_matches_retained_e1(self):
        packet = build_sample_noargs_packet("sample_noop")
        self.assertEqual(packet, build_sample_noop_packet())
        self.assertEqual(packet.hex(), "18fac000000100dc")
        self.assertEqual(
            hashlib.sha256(packet).hexdigest(),
            "722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd",
        )

    def test_reset_counters_packet_is_deterministic(self):
        packet = build_sample_noargs_packet("sample_reset_counters")
        self.assertEqual(packet.hex(), "18fac000000101dd")
        self.assertEqual(
            hashlib.sha256(packet).hexdigest(),
            "c8a8692bad90aab74ffe550c87e93ed83838d4b4f45c57a609a00455292d41cb",
        )

    def test_e1_envelope_remains_noop_compatible(self):
        envelope = build_e1_envelope("modeled_attacker")
        self.assertEqual(envelope["command_class"], "sample_noop")
        self.assertEqual(
            envelope["packet_hex"],
            build_sample_noop_packet().hex(),
        )

    def test_p0_forwards_both_command_classes(self):
        for command_class in ("sample_reset_counters", "sample_noop"):
            with self.subTest(command_class=command_class):
                self.assertTrue(
                    decide_forward(
                        "OBSERVE_ONLY",
                        build_command_envelope(
                            "modeled_attacker",
                            command_class,
                        ),
                    )
                )

    def test_p1_source_isolation_behavior_is_preserved(self):
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

    def test_p2_blocks_only_restricted_command_class(self):
        self.assertFalse(
            decide_forward(
                "RESTRICT_HIGH_RISK_COMMANDS",
                build_command_envelope(
                    "modeled_attacker",
                    "sample_reset_counters",
                ),
            )
        )
        self.assertTrue(
            decide_forward(
                "RESTRICT_HIGH_RISK_COMMANDS",
                build_command_envelope(
                    "modeled_attacker",
                    "sample_noop",
                ),
            )
        )

    def test_p2_is_command_class_not_source_based(self):
        for source_id in ("modeled_attacker", "authorized_ground"):
            with self.subTest(source_id=source_id):
                self.assertFalse(
                    decide_forward(
                        "RESTRICT_HIGH_RISK_COMMANDS",
                        build_command_envelope(
                            source_id,
                            "sample_reset_counters",
                        ),
                    )
                )

    def test_p4_blocks_routine_commands_from_both_sources(self):
        for source_id in ("modeled_attacker", "authorized_ground"):
            with self.subTest(source_id=source_id):
                self.assertFalse(
                    decide_forward(
                        "ENTER_SAFE_MODE",
                        build_e1_envelope(source_id),
                    )
                )

    def test_unsupported_action_rejected(self):
        with self.assertRaises(ValueError):
            decide_forward(
                "REQUEST_VERIFIED_ROLLBACK",
                build_e1_envelope("modeled_attacker"),
            )


if __name__ == "__main__":
    unittest.main()
