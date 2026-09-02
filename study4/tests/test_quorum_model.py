import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quorum_model import Rule, Scenario, evaluate, rules, run_population  # noqa: E402


class Study4QuorumTests(unittest.TestCase):
    def test_population(self) -> None:
        self.assertEqual(len(run_population()), 4608)

    def test_rule_count(self) -> None:
        self.assertEqual(len(rules()), 18)

    def test_safety_zero_compromise_is_safe(self) -> None:
        rows = [
            row
            for row in run_population()
            if row.block == "SAFETY" and row.affected_count == 0
        ]
        self.assertTrue(all(not row.unsafe_qualified for row in rows))

    def test_availability_zero_loss_is_available(self) -> None:
        rows = [
            row
            for row in run_population()
            if row.block == "AVAILABILITY" and row.affected_count == 0
        ]
        self.assertTrue(all(not row.false_conservative for row in rows))

    def test_provenance_diversity_blocks_same_domain_pair(self) -> None:
        same_domain = Scenario("SAFETY", ("P1", "P2"), 2)
        self.assertTrue(evaluate(Rule(2, 1), same_domain).unsafe_qualified)
        self.assertFalse(evaluate(Rule(2, 2), same_domain).unsafe_qualified)

    def test_absolute_quorum_fails_closed_on_unavailability(self) -> None:
        row = evaluate(Rule(7, 3), Scenario("AVAILABILITY", ("P1",), 1))
        self.assertTrue(row.false_conservative)


if __name__ == "__main__":
    unittest.main()
