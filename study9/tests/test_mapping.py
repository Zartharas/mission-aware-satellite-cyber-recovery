from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT / "study9" / "src", ROOT / "study2" / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import unittest

from study9_semantic.contracts import FROZEN_DATASET_IDS, REQUIRED_VARIABLES
from study9_semantic.mapping import materialize_mapping_matrix, records_for_dataset


class MappingTests(unittest.TestCase):
    def test_exact_three_by_eight_matrix(self):
        rows = materialize_mapping_matrix()
        self.assertEqual(len(rows), 24)
        self.assertEqual(
            {(row.dataset_id, row.recovery_state_variable) for row in rows},
            {(dataset, variable) for dataset in FROZEN_DATASET_IDS for variable in REQUIRED_VARIABLES},
        )

    def test_no_active_direct_mapping_after_unsw_domain_deviation(self):
        rows = materialize_mapping_matrix()
        direct = [row for row in rows if row.mapping_class == "DIRECT"]
        self.assertEqual(direct, [])
        unsw = records_for_dataset("UNSW_IOTSAT_2026", rows)
        security_signal = next(
            row for row in unsw if row.recovery_state_variable == "security_signal"
        )
        self.assertEqual(security_signal.mapping_class, "AMBIGUOUS")
        self.assertEqual(security_signal.native_field_names, ("Position_Anomaly",))
        self.assertIsNone(security_signal.value_rule)
        self.assertIn("72 of 404798", security_signal.semantic_rationale)

    def test_attack_labels_never_become_operational_mapping_fields(self):
        rows = materialize_mapping_matrix()
        forbidden = {
            "Label",
            "attacks.cpuhightarget.duration",
            "attacks.cpuhightarget.target",
            "Attack_Flag",
            "Attack_Type",
            "Attack_Subtype",
            "Attack_Severity",
            "Attack_Duration",
            "Attack_Source_Type",
            "Detection_Confidence",
            "Attack_Timeline_ID",
            "CCSDS_MC_Frame_Count",
            "CCSDS_Packet_Sequence_Count",
            "CCSDS_APID",
        }
        for row in rows:
            self.assertTrue(forbidden.isdisjoint(row.native_field_names))

    def test_each_dataset_keeps_frozen_variable_order(self):
        for dataset in FROZEN_DATASET_IDS:
            rows = records_for_dataset(dataset)
            self.assertEqual(tuple(row.recovery_state_variable for row in rows), REQUIRED_VARIABLES)


if __name__ == "__main__":
    unittest.main()
