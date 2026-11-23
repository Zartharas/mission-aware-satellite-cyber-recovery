"""Repository-native tests using the exact blob-pinned Study 10 G1 synthetic fixture.

All inputs are publicly documented synthetic claims, not real source telemetry.
"""
from __future__ import annotations

import ast
import copy
from pathlib import Path
import unittest

from g3_independent_oracle import FIELDS, POLICIES, IncompleteObservation, oracle_action
from g3_synthetic_parity import (
    EXPECTED_CASES, G3_CASES, G3Failure, TIME_ONLY_CASES,
    _production_action, case_suite, exhaustive_parity, load_contract,
    load_frozen_selector, mutate, project_synthetic, read_pinned,
    static_six_examples,
)

ROOT = Path(__file__).resolve().parents[1]


class G3FrozenIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture, cls.manifest, cls.inventory = load_contract(read_pinned(ROOT))
        cls.production = load_frozen_selector(ROOT)

    def test_exact_frozen_p0(self):
        self.assertEqual(
            tuple(project_synthetic(self.fixture).values()),
            (True, True, True, True, False, True, False, True),
        )

    def test_pins_18_cases_in_exact_original_order(self):
        self.assertEqual(len(G3_CASES), 18)
        self.assertEqual(set(G3_CASES), set(EXPECTED_CASES))
        self.assertEqual(
            tuple(self.manifest["synthetic_controls"]["mutation_case_ids"]), G3_CASES,
        )

    def test_18_synthetic_cases_all_pass(self):
        result, calls, errors = case_suite(self.fixture, self.production)
        self.assertEqual(len(result), 18)
        self.assertTrue(all(x["status"].startswith("PASS") for x in result))
        self.assertEqual(calls, 20)
        self.assertEqual(errors, [])

    def test_frozen_six_static_selector_examples(self):
        comparisons, errors = static_six_examples(self.inventory, self.production)
        self.assertEqual(comparisons, 24)
        self.assertEqual(errors, [])

    def test_four_policy_exhaustive_256_states(self):
        comparisons, errors, digest, counts = exhaustive_parity(self.production)
        self.assertEqual(comparisons, 1024)
        self.assertEqual(errors, [])
        self.assertEqual(counts, dict.fromkeys(POLICIES, 256))
        self.assertEqual(len(digest), 64)

    def test_boundary_cases_are_isolated_not_full_selector_states(self):
        checks, _, errors = case_suite(self.fixture, self.production)
        self.assertEqual(errors, [])
        self.assertTrue(all(x["selector_calls"] == 0 for x in checks if x["id"] in TIME_ONLY_CASES))

    def test_inclusive_time_endpoints_and_outer_failures(self):
        expected = {
            "S10_SYN_T_LOWER": True,
            "S10_SYN_T_UPPER": True,
            "S10_SYN_N_FUTURE_ISSUE": False,
            "S10_SYN_N_EXPIRED": False,
        }
        for case_id, value in expected.items():
            with self.subTest(case=case_id):
                self.assertIs(project_synthetic(mutate(self.fixture, case_id))["fresh"], value)

    def test_known_negative_vs_unknown_epoch(self):
        self.assertIs(
            project_synthetic(mutate(self.fixture, "S10_SYN_N_EPOCH_MISMATCH"))["epoch_valid"],
            False,
        )
        self.assertIsNone(
            project_synthetic(mutate(self.fixture, "S10_SYN_N_EPOCH_UNKNOWN"))["epoch_valid"],
        )

    def test_accepted_criterion_requires_expected_value_not_only_presence(self):
        self.assertIs(
            project_synthetic(mutate(self.fixture, "S10_SYN_N_CRITERIA_VALUE"))[
                "minimum_evidence_complete"
            ],
            False,
        )

    def test_missing_criterion_with_complete_vs_incomplete_ledger(self):
        known_absent = project_synthetic(mutate(self.fixture, "S10_SYN_N_CRITERIA"))
        unknown = project_synthetic(mutate(self.fixture, "S10_SYN_N_LEDGER_INCOMPLETE"))
        self.assertIs(known_absent["minimum_evidence_complete"], False)
        self.assertIsNone(unknown["minimum_evidence_complete"])

    def test_accepted_same_subject_key_epoch_claim_conflict(self):
        value = project_synthetic(mutate(self.fixture, "S10_SYN_N_CONTRADICTION"))
        self.assertIs(value["contradictory"], True)

    def test_crc_and_apid_substitutions_fail_closed(self):
        self.assertIsNone(
            project_synthetic(mutate(self.fixture, "S10_SYN_N_CRC"))["signature_valid"]
        )
        self.assertIsNone(
            project_synthetic(mutate(self.fixture, "S10_SYN_N_APID"))["source_trusted"]
        )

    def test_offline_label_command_and_missing_inputs_not_coerced(self):
        checks = (
            ("S10_SYN_N_LABEL", "security_signal"),
            ("S10_SYN_N_COMMAND", "authorization_available"),
            ("S10_SYN_N_TIME", "fresh"),
        )
        for case, field in checks:
            with self.subTest(case=case):
                observed = project_synthetic(mutate(self.fixture, case))
                self.assertIsNone(observed[field])
                for policy in POLICIES:
                    with self.assertRaises(IncompleteObservation):
                        oracle_action(policy, observed)
                    with self.assertRaises(IncompleteObservation):
                        _production_action(self.production, policy, observed)

    def test_all_missing_is_unknown_for_every_variable(self):
        observed = project_synthetic(mutate(self.fixture, "S10_SYN_N_MISSING"))
        self.assertEqual(tuple(observed), FIELDS)
        self.assertTrue(all(value is None for value in observed.values()))

    def test_population_mixing_is_rejected_before_selector(self):
        self.assertIsNone(mutate(self.fixture, "S10_SYN_N_MIXING"))

    def test_duplicate_claim_ids_are_not_silent(self):
        f = copy.deepcopy(self.fixture)
        f["accepted_claims"]["claims"][1]["claim_id"] = f["accepted_claims"]["claims"][0]["claim_id"]
        with self.assertRaises(G3Failure):
            project_synthetic(f)

    def test_source_claim_count_mismatch_rejected(self):
        f = copy.deepcopy(self.fixture)
        f["accepted_claims"]["current_claims_count"] = 99
        with self.assertRaises(G3Failure):
            project_synthetic(f)

    def test_real_signature_verification_not_claimed(self):
        f = copy.deepcopy(self.fixture)
        f["cryptographic_check"]["real_signature_verified"] = True
        with self.assertRaises(G3Failure):
            project_synthetic(f)

    def test_unknown_and_integer_boolean_coercion_rejected(self):
        complete = project_synthetic(self.fixture)
        for v in (None, 0, 1, "unknown"):
            for policy in POLICIES:
                sample = dict(complete)
                sample["signature_valid"] = v
                with self.assertRaises(IncompleteObservation):
                    oracle_action(policy, sample)

    def test_frozen_ablations_excluded(self):
        with self.assertRaises(ValueError):
            oracle_action("S2_ABL_NO_FRESHNESS", project_synthetic(self.fixture))

    def test_independent_oracle_source_has_no_study2_import(self):
        source = (ROOT / "study10/g3_independent_oracle.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = [
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        ]
        imports.extend(
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        )
        self.assertFalse(any(name.startswith("study2") for name in imports))

    def test_deliberately_incorrect_selector_is_detected(self):
        prod = self.production

        class AlwaysProceed:
            Study2Policy = prod.Study2Policy
            ObservationSummary = prod.ObservationSummary

            class Result:
                value = "PROCEED_TO_RECOVERY_GATE"

            @staticmethod
            def select_action(policy, obs):
                return AlwaysProceed.Result()

        count, errors, _, _ = exhaustive_parity(AlwaysProceed)
        self.assertEqual(count, 1024)
        self.assertGreater(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
