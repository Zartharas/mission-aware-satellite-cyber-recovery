from __future__ import annotations

from collections import defaultdict
import unittest

from study5.src.bridge_model import LABELS, REQUIRED_RECOVERY_INPUTS, SELECTOR_SHA256, portability_rows, selector_sha256, sufficiency_rows, transferability_rows


class Study5BridgeTests(unittest.TestCase):
    def test_frozen_selector_dependency(self) -> None:
        self.assertEqual(selector_sha256(), SELECTOR_SHA256)

    def test_exact_population(self) -> None:
        rows = portability_rows()
        self.assertEqual(len(rows), 80)
        self.assertEqual(len({(r["label_code"], r["context"], r["policy"]) for r in rows}), 80)

    def test_external_label_schema(self) -> None:
        self.assertEqual(LABELS, ((0, "COMMAND_FLOODING"), (1, "DATA_INJECTION"), (2, "DEFENCE_IMPAIRMENT"), (3, "NORMAL"), (4, "STORAGE_EXHAUSTION")))

    def test_no_direct_recovery_inputs(self) -> None:
        rows = sufficiency_rows()
        self.assertEqual(len(rows), len(REQUIRED_RECOVERY_INPUTS))
        self.assertEqual(sum(bool(r["directly_available_from_cucdid_row"]) for r in rows), 0)
        signal = next(r for r in rows if r["required_input"] == "security_signal")
        self.assertEqual(signal["allowed_study5_source"], "OFFLINE_LABEL_ORACLE")

    def test_attack_subtype_action_invariance(self) -> None:
        attacks = {"COMMAND_FLOODING", "DATA_INJECTION", "DEFENCE_IMPAIRMENT", "STORAGE_EXHAUSTION"}
        grouped: dict[tuple[str, str], set[str]] = defaultdict(set)
        for row in portability_rows():
            if row["label"] in attacks:
                grouped[(str(row["context"]), str(row["policy"]))].add(str(row["action"]))
        self.assertEqual(len(grouped), 16)
        self.assertTrue(all(len(actions) == 1 for actions in grouped.values()))

    def test_transferability_is_not_falsely_direct(self) -> None:
        rows = transferability_rows()
        self.assertEqual(len(rows), 5)
        for row in rows:
            if row["label"] != "NORMAL":
                self.assertNotEqual(row["frozen_event_correspondence"], "DIRECT")
                self.assertNotEqual(row["study2_correspondence"], "DIRECT")


if __name__ == "__main__":
    unittest.main()
