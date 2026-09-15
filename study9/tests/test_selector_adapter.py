from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT / "study9" / "src", ROOT / "study2" / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import itertools
import unittest
from unittest.mock import patch

from study9_semantic.contracts import REQUIRED_VARIABLES, load_frozen_contracts
from study9_semantic.selector_adapter import (
    clear_selector_caches,
    select_action_from_state,
    selector_types,
)


class SelectorAdapterTests(unittest.TestCase):
    def tearDown(self):
        clear_selector_caches()

    def test_adapter_matches_frozen_selector_for_every_binary_state_and_policy(self):
        frozen_contracts = load_frozen_contracts(ROOT)
        clear_selector_caches()
        with patch(
            "study9_semantic.selector_adapter.load_frozen_contracts",
            return_value=frozen_contracts,
        ) as loader:
            Study2Policy, _, ObservationSummary = selector_types()
            from study2_security.selectors import select_action

            for bits in itertools.product((False, True), repeat=len(REQUIRED_VARIABLES)):
                state = dict(zip(REQUIRED_VARIABLES, bits, strict=True))
                obs = ObservationSummary(**state)
                for policy in Study2Policy:
                    self.assertEqual(
                        select_action_from_state(policy, state),
                        select_action(policy, obs),
                    )

            self.assertEqual(
                loader.call_count,
                1,
                "exhaustive selector equivalence must validate frozen contracts only once",
            )

    def test_adapter_rejects_incomplete_state(self):
        Study2Policy, _, _ = selector_types()
        with self.assertRaises(ValueError):
            select_action_from_state(Study2Policy.EVIDENCE_AWARE, {"signature_valid": True})


if __name__ == "__main__":
    unittest.main()
