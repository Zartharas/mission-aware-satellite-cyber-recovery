from __future__ import annotations

import unittest

from study2_security.attempt_ledger import INVALID, VALID, next_required_trial, validate_attempt_ledger


class AttemptLedgerTests(unittest.TestCase):
    def _attempt(self, *, run_id: str, status: str, trial_id: str = "S2-AEATR-001:A01:2100001", cell_id: str = "A01", seed: int = 2_100_001) -> dict[str, object]:
        return {"run_id": run_id, "attempt_status": status, "trial_id": trial_id, "cell_id": cell_id, "seed": seed}

    def test_invalid_attempt_is_retained_without_advancing(self) -> None:
        attempts = [self._attempt(run_id="RUN-1", status=INVALID)]
        state = validate_attempt_ledger(attempts)
        self.assertEqual(state["valid_position_count"], 0)
        self.assertEqual(state["invalid_attempt_count"], 1)
        self.assertEqual(next_required_trial(attempts)["trial_id"], "S2-AEATR-001:A01:2100001")

    def test_valid_attempt_advances_exactly_one_position(self) -> None:
        attempts = [self._attempt(run_id="RUN-1", status=VALID)]
        state = validate_attempt_ledger(attempts)
        self.assertEqual(state["valid_position_count"], 1)
        self.assertEqual(next_required_trial(attempts)["trial_id"], "S2-AEATR-001:A01:2100002")

    def test_duplicate_run_id_fails_closed(self) -> None:
        attempts = [self._attempt(run_id="RUN-1", status=INVALID), self._attempt(run_id="RUN-1", status=VALID)]
        with self.assertRaises(ValueError):
            validate_attempt_ledger(attempts)

    def test_skipping_frozen_position_fails_closed(self) -> None:
        attempt = self._attempt(run_id="RUN-2", status=VALID, trial_id="S2-AEATR-001:A01:2100002", seed=2_100_002)
        with self.assertRaises(ValueError):
            validate_attempt_ledger([attempt])


if __name__ == "__main__":
    unittest.main()
