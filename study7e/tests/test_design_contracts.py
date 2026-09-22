from __future__ import annotations

import unittest

from study7e.src.aerc_design import (
    BASE_FEATURES,
    EXTENDED_FEATURES,
    PRIVILEGED_FIELDS,
    affected_paths,
    build_scenario_manifest,
    d0_base,
    d1_corroborated,
    domain_map,
    manifest_counts,
    objective_action,
    paired_input_hashes,
    project_base,
    project_corroborated,
)


class Study7EDesignTests(unittest.TestCase):
    def test_topology_alias_semantics(self) -> None:
        t0 = domain_map("T0_SHARED_ALL")
        for domain in t0["primary"]:
            self.assertEqual(t0["primary"][domain], t0["corroborator"][domain])

        t4 = domain_map("T4_SEPARATE_ALL")
        for domain in t4["primary"]:
            self.assertNotEqual(t4["primary"][domain], t4["corroborator"][domain])

        t2 = domain_map("T2_SEPARATE_SOURCE_KEY_EXEC")
        for domain in ("source", "key", "execution"):
            self.assertNotEqual(t2["primary"][domain], t2["corroborator"][domain])
        for domain in ("transport", "authority"):
            self.assertEqual(t2["primary"][domain], t2["corroborator"][domain])

    def test_fault_propagation_uses_aliasing(self) -> None:
        self.assertEqual(affected_paths("T0_SHARED_ALL", "F3"), frozenset({"primary", "corroborator"}))
        self.assertEqual(affected_paths("T2_SEPARATE_SOURCE_KEY_EXEC", "F3"), frozenset({"primary"}))
        self.assertEqual(affected_paths("T3_SEPARATE_THROUGH_TRANSPORT", "F10"), frozenset({"primary", "corroborator"}))
        self.assertEqual(affected_paths("T4_SEPARATE_ALL", "F10"), frozenset({"primary"}))
        self.assertEqual(affected_paths("T4_SEPARATE_ALL", "F5"), frozenset({"primary"}))
        self.assertEqual(affected_paths("T0_SHARED_ALL", "F0"), frozenset())

    def test_manifest_cardinality(self) -> None:
        rows = build_scenario_manifest()
        counts = manifest_counts(rows)
        self.assertEqual(counts["TR"], 72)
        self.assertEqual(counts["E1"], 72)
        self.assertEqual(counts["E2"], 96)
        self.assertEqual(counts["C0"], 20)
        self.assertEqual(counts["TOTAL"], 260)
        self.assertEqual(counts["CANONICAL_EVAL_SCENARIOS"], 188)
        self.assertEqual(counts["CANONICAL_EVAL_POLICY_DECISIONS"], 752)
        self.assertEqual(len({row.scenario_id for row in rows}), 260)

    def test_training_and_eval_partition(self) -> None:
        rows = build_scenario_manifest()
        training = [r for r in rows if r.block == "TR"]
        evaluation = [r for r in rows if r.block != "TR"]
        self.assertEqual(len(training), 72)
        self.assertEqual(len(evaluation), 188)
        self.assertFalse({r.scenario_id for r in training} & {r.scenario_id for r in evaluation})

    def test_objective_action(self) -> None:
        rows = build_scenario_manifest()
        for row in rows:
            expected = (
                "ENTER_RECOVERY_GATE"
                if row.security_signal and row.true_authorization and row.true_health_ready
                else "HOLD"
            )
            self.assertEqual(objective_action(row), expected)

    def _all_true_snapshot(self) -> dict[str, int]:
        return {feature: 1 for feature in EXTENDED_FEATURES}

    def test_equal_information_hashes(self) -> None:
        hashes = paired_input_hashes(self._all_true_snapshot())
        self.assertEqual(hashes["D0_BASE"], hashes["L0_BASE"])
        self.assertEqual(hashes["D1_CORROBORATED"], hashes["L1_CORROBORATED"])
        self.assertNotEqual(hashes["D0_BASE"], hashes["D1_CORROBORATED"])

    def test_privileged_fields_rejected(self) -> None:
        snapshot = self._all_true_snapshot()
        for forbidden in PRIVILEGED_FIELDS:
            poisoned = dict(snapshot)
            poisoned[forbidden] = 1
            with self.assertRaises(ValueError):
                project_base(poisoned)
            with self.assertRaises(ValueError):
                project_corroborated(poisoned)

    def test_feature_schema_lengths(self) -> None:
        self.assertEqual(len(BASE_FEATURES), 9)
        self.assertEqual(len(EXTENDED_FEATURES), 16)

    def test_deterministic_policy_contracts(self) -> None:
        all_true = self._all_true_snapshot()
        base = project_base(all_true)
        corr = project_corroborated(all_true)
        self.assertEqual(d0_base(base), "ENTER_RECOVERY_GATE")
        self.assertEqual(d1_corroborated(corr), "ENTER_RECOVERY_GATE")

        base_auth_false = dict(all_true)
        base_auth_false["primary_authorization"] = 0
        self.assertEqual(d0_base(project_base(base_auth_false)), "HOLD")

        corr_auth_false = dict(all_true)
        corr_auth_false["corr_authorization"] = 0
        self.assertEqual(d1_corroborated(project_corroborated(corr_auth_false)), "HOLD")

    def test_no_canonical_scientific_runner_is_exposed(self) -> None:
        import study7e.src.aerc_design as module

        prohibited = {
            "run_canonical_execution",
            "write_canonical_results",
            "freeze_canonical_models",
        }
        self.assertFalse(prohibited.intersection(dir(module)))


if __name__ == "__main__":
    unittest.main()
