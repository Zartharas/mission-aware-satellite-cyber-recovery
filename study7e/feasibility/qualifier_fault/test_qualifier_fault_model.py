from __future__ import annotations

import inspect
import unittest
from dataclasses import replace

from study7e.src.aerc_design import (
    FAULT_PROFILES,
    PRIVILEGED_FIELDS,
    TOPOLOGY_SEPARATION,
    affected_paths,
)
from study7e.feasibility.qualifier_fault.qualifier_fault_model import (
    PathState,
    ZERO_FEATURES,
    apply_fault,
    changed_paths,
    default_context,
    nominal_evidence,
    qualify_evidence,
    qualify_stream,
)


class QualifierFaultContractTests(unittest.TestCase):
    def test_qualifier_api_contains_no_research_truth_inputs(self) -> None:
        names = set(inspect.signature(qualify_evidence).parameters)
        self.assertTrue(PRIVILEGED_FIELDS.isdisjoint(names))
        self.assertNotIn("fault_profile", names)
        self.assertNotIn("topology", names)

    def test_absent_evidence_is_all_zero(self) -> None:
        features, state = qualify_evidence(None, default_context(), PathState())
        self.assertEqual(features, ZERO_FEATURES)
        self.assertEqual(state, PathState())

    def test_wrong_scenario_is_nonapplicable(self) -> None:
        evidence = replace(nominal_evidence("primary", 1), scenario_id=0xDEADBEEF)
        features, state = qualify_evidence(evidence, default_context(), PathState())
        self.assertEqual(features, ZERO_FEATURES)
        self.assertEqual(state, PathState())

    def test_invalid_signature_preserves_independent_authorization_claim(self) -> None:
        evidence = replace(nominal_evidence("primary", 1), signature_valid=0)
        features, state = qualify_evidence(evidence, default_context(), PathState())
        self.assertEqual(features["complete"], 1)
        self.assertEqual(features["authorization"], 1)
        self.assertEqual(features["signature_valid"], 0)
        self.assertEqual(features["source_trusted"], 1)
        self.assertEqual(features["fresh"], 1)
        self.assertEqual(features["epoch_valid"], 1)
        self.assertEqual(state, PathState())

    def test_freshness_boundary_is_parameterized(self) -> None:
        context = default_context(now_tick=100, freshness_max_age_ticks=5)
        fresh = replace(nominal_evidence("primary", 1), issued_tick=95)
        stale = replace(nominal_evidence("primary", 1), issued_tick=94)
        future = replace(nominal_evidence("primary", 1), issued_tick=101)
        self.assertEqual(qualify_evidence(fresh, context, PathState())[0]["fresh"], 1)
        self.assertEqual(qualify_evidence(stale, context, PathState())[0]["fresh"], 0)
        self.assertEqual(qualify_evidence(future, context, PathState())[0]["fresh"], 0)

    def test_equal_identical_duplicate_is_idempotent(self) -> None:
        evidence = nominal_evidence("primary", 1)
        first_features, state = qualify_evidence(evidence, default_context(), PathState())
        second_features, state2 = qualify_evidence(evidence, default_context(), state)
        self.assertEqual(first_features["noncontradictory"], 1)
        self.assertEqual(second_features["noncontradictory"], 1)
        self.assertEqual(state2.last_sequence, 1)
        self.assertFalse(state2.contradicted)

    def test_same_sequence_different_body_is_sticky_contradiction(self) -> None:
        first = nominal_evidence("primary", 1)
        second = replace(first, authorization=0)
        _, state = qualify_evidence(first, default_context(), PathState())
        features, state = qualify_evidence(second, default_context(), state)
        self.assertEqual(features["signature_valid"], 1)
        self.assertEqual(features["authorization"], 0)
        self.assertEqual(features["noncontradictory"], 0)
        self.assertTrue(state.contradicted)
        third = replace(first, sequence=2)
        features, state = qualify_evidence(third, default_context(), state)
        self.assertEqual(features["noncontradictory"], 0)
        self.assertTrue(state.contradicted)

    def test_lower_sequence_sets_replay_inconsistency(self) -> None:
        first = replace(nominal_evidence("primary", 1), sequence=2)
        replay = replace(first, sequence=1)
        _, state = qualify_evidence(first, default_context(), PathState())
        features, state = qualify_evidence(replay, default_context(), state)
        self.assertEqual(features["noncontradictory"], 0)
        self.assertEqual(state.last_sequence, 2)
        self.assertTrue(state.contradicted)

    def test_invalid_signature_does_not_advance_authenticated_sequence(self) -> None:
        invalid = replace(nominal_evidence("primary", 1), sequence=9, signature_valid=0)
        _, state = qualify_evidence(invalid, default_context(), PathState())
        self.assertIsNone(state.last_sequence)
        self.assertFalse(state.contradicted)

    def test_fault_contract_profile_set_matches_design(self) -> None:
        self.assertEqual(set(FAULT_PROFILES), {f"F{i}" for i in range(13)})

    def test_fault_topology_propagation_matches_existing_design(self) -> None:
        for topology in TOPOLOGY_SEPARATION:
            for fault_profile in FAULT_PROFILES:
                with self.subTest(topology=topology, fault_profile=fault_profile):
                    streams = apply_fault(topology, fault_profile, 1)
                    self.assertEqual(
                        changed_paths(streams, 1),
                        affected_paths(topology, fault_profile),
                    )

    def test_f5_primary_freshness_delay_only_changes_fresh(self) -> None:
        streams = apply_fault("T4_SEPARATE_ALL", "F5", 1)
        features, _ = qualify_stream(streams["primary"], default_context())
        self.assertEqual(features["signature_valid"], 1)
        self.assertEqual(features["source_trusted"], 1)
        self.assertEqual(features["fresh"], 0)
        self.assertEqual(features["epoch_valid"], 1)
        self.assertEqual(features["complete"], 1)
        self.assertEqual(features["authorization"], 1)

    def test_f9_transport_mutation_is_signature_and_epoch_invalid(self) -> None:
        streams = apply_fault("T4_SEPARATE_ALL", "F9", 1)
        features, state = qualify_stream(streams["primary"], default_context())
        self.assertEqual(features["signature_valid"], 0)
        self.assertEqual(features["epoch_valid"], 0)
        self.assertEqual(features["authorization"], 1)
        self.assertEqual(features["complete"], 1)
        self.assertIsNone(state.last_sequence)

    def test_f11_compound_preserves_false_claim_and_invalidates_signature_epoch(self) -> None:
        streams = apply_fault("T4_SEPARATE_ALL", "F11", 1)
        features, _ = qualify_stream(streams["primary"], default_context())
        self.assertEqual(features["authorization"], 0)
        self.assertEqual(features["signature_valid"], 0)
        self.assertEqual(features["epoch_valid"], 0)

    def test_f12_execution_equivocation_drives_noncontradictory_zero(self) -> None:
        streams = apply_fault("T4_SEPARATE_ALL", "F12", 1)
        self.assertEqual(len(streams["primary"]), 2)
        features, state = qualify_stream(streams["primary"], default_context())
        self.assertEqual(features["signature_valid"], 1)
        self.assertEqual(features["authorization"], 0)
        self.assertEqual(features["noncontradictory"], 0)
        self.assertTrue(state.contradicted)

    def test_t0_shared_domains_propagate_domain_faults_to_both_paths(self) -> None:
        for fault_profile in ("F1", "F3", "F9", "F10", "F12"):
            with self.subTest(fault_profile=fault_profile):
                self.assertEqual(
                    affected_paths("T0_SHARED_ALL", fault_profile),
                    frozenset({"primary", "corroborator"}),
                )

    def test_t4_separate_domains_keep_targeted_faults_path_local(self) -> None:
        for fault_profile in ("F1", "F3", "F9", "F10", "F12"):
            with self.subTest(fault_profile=fault_profile):
                self.assertEqual(
                    affected_paths("T4_SEPARATE_ALL", fault_profile),
                    frozenset({"primary"}),
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
