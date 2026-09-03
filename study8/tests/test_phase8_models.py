from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIMARY_PATH = ROOT / "study8" / "src" / "contact_recovery_model.py"
AUDITOR_PATH = ROOT / "study8" / "audit" / "independent_reference.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


primary = _load("study8_primary", PRIMARY_PATH)
auditor = _load("study8_independent", AUDITOR_PATH)


class Phase8ImplementationTests(unittest.TestCase):
    def test_population_shape_only(self) -> None:
        cases = primary.factor_population()
        self.assertEqual(len(cases), 3456)
        self.assertEqual(len(set(cases)), 3456)

    def test_contact_schedules_are_unique_and_equal_capacity(self) -> None:
        schedules = {
            (regime, phase): primary.materialize_contacts(regime, phase)
            for regime in primary.BASE_CONTACTS
            for phase in primary.PHASE_OFFSETS
        }
        self.assertEqual(len(schedules), 24)
        self.assertEqual(len({schedule for schedule in schedules.values()}), 24)
        self.assertTrue(
            all(sum(capacity for _, capacity in schedule) == 65536 for schedule in schedules.values())
        )

    def test_primary_and_independent_fixture_parity(self) -> None:
        for case in primary.development_fixture_cases():
            actual = primary.evaluate_case(case)
            expected = auditor.independently_recompute_case(actual)
            self.assertEqual(actual, expected)

    def test_direct_entrypoints_refuse_execution(self) -> None:
        primary_text = PRIMARY_PATH.read_text(encoding="utf-8")
        auditor_text = AUDITOR_PATH.read_text(encoding="utf-8")
        self.assertIn("direct or canonical execution is not authorized", primary_text)
        self.assertIn("artifact audit execution is not authorized", auditor_text)

    def test_hybrid_policy_has_explicit_overlap_endpoint(self) -> None:
        case = primary.Case(
            "PROFILE_768_65",
            "P2_HYBRID_OVERLAP",
            "R3_SPARSE_LARGE",
            "A2_DELAY_FIRST_TRANSITION_PROOF_ONE_CONTACT",
            2,
            48,
        )
        row = primary.evaluate_case(case)
        self.assertIn("dual_epoch_overlap_slots", row)
        self.assertGreaterEqual(row["dual_epoch_overlap_slots"], 0)

    def test_structural_zero_safety_outputs_in_fixtures(self) -> None:
        for case in primary.development_fixture_cases():
            row = primary.evaluate_case(case)
            self.assertEqual(row["rollback_invoked"], 0)
            self.assertEqual(row["stale_epoch_acceptance"], 0)


if __name__ == "__main__":
    unittest.main()
