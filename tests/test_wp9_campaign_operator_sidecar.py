from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = ROOT / "ops" / "wp9_campaign_operator.py"


def _load_operator():
    spec = importlib.util.spec_from_file_location(
        "wp9_campaign_operator_sidecar",
        OPERATOR,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load sidecar operator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestWp9CampaignOperatorSidecar(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.operator = _load_operator()

    def test_runtime_identity_is_frozen_to_position_1_baseline(self) -> None:
        self.assertEqual(
            self.operator.FROZEN_RUNTIME_SHA,
            "aae2239753119c92e7633db3b6c73aee94c7b6dd",
        )
        self.assertEqual(
            self.operator.FROZEN_RUNTIME_TREE,
            "105bc8a868ab90e0c1cfd2385e4e0b50924312df",
        )
        self.assertFalse(self.operator.AUTOMATIC_RETRY_ALLOWED)
        self.assertFalse(self.operator.AUTOMATIC_NEXT_ALLOWED)

    def test_position_1_valid_history_resolves_position_2(self) -> None:
        history = [
            {
                "campaign_seed": 10001,
                "cell_order_index": 1,
                "cell_id": "A19",
                "run_id": "position-1-valid",
                "attempt_status": "VALID",
            }
        ]
        next_trial = self.operator.next_required_trial(
            repo_root=ROOT,
            history=history,
        )
        self.assertEqual(next_trial["global_order_index"], 2)
        self.assertEqual(next_trial["campaign_seed"], 10001)
        self.assertEqual(next_trial["cell_order_index"], 2)
        self.assertEqual(next_trial["cell_id"], "A13")

    def test_unledgered_plan_request_only_is_pre_runtime_unconsumed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "run"
            ground = evidence / "immutable-ground"
            ground.mkdir(parents=True)
            (ground / "campaign-plan.json").write_text("{}\n", encoding="utf-8")
            (ground / "r066-runtime-request.json").write_text("{}\n", encoding="utf-8")
            result = self.operator.classify_unledgered_evidence(evidence)
            self.assertEqual(result, "PRE_RUNTIME_ABORT_UNCONSUMED")

    def test_unledgered_seed_commit_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "run"
            ground = evidence / "immutable-ground"
            ground.mkdir(parents=True)
            (ground / "campaign-seed-consumption.json").write_text(
                "{}\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                self.operator.classify_unledgered_evidence(evidence)

    def test_unledgered_canonical_result_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "run"
            evidence.mkdir(parents=True)
            (evidence / "campaign-trial-result.json").write_text(
                "{}\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                self.operator.classify_unledgered_evidence(evidence)

    def test_atomic_history_append_advances_exactly_one_position(self) -> None:
        history = [
            {
                "campaign_seed": 10001,
                "cell_order_index": 1,
                "cell_id": "A19",
                "run_id": "position-1-valid",
                "attempt_status": "VALID",
            }
        ]
        entry = {
            "campaign_seed": 10001,
            "cell_order_index": 2,
            "cell_id": "A13",
            "run_id": "position-2-valid",
            "attempt_status": "VALID",
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "attempt-history.json"
            path.write_text(json.dumps(history) + "\n", encoding="utf-8")
            state = self.operator.append_attempt_history_atomic(
                repo_root=ROOT,
                history_path=path,
                entry=entry,
            )
            retained = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(len(retained), 2)
            self.assertEqual(state["valid_position_count"], 2)
            self.assertEqual(state["attempt_count"], 2)
            next_trial = self.operator.next_required_trial(
                repo_root=ROOT,
                history=retained,
            )
            self.assertEqual(next_trial["global_order_index"], 3)

    def test_invalid_attempt_retains_same_frozen_position(self) -> None:
        history = [
            {
                "campaign_seed": 10001,
                "cell_order_index": 1,
                "cell_id": "A19",
                "run_id": "position-1-valid",
                "attempt_status": "VALID",
            },
            {
                "campaign_seed": 10001,
                "cell_order_index": 2,
                "cell_id": "A13",
                "run_id": "position-2-invalid",
                "attempt_status": "INVALID",
            },
        ]
        next_trial = self.operator.next_required_trial(
            repo_root=ROOT,
            history=history,
        )
        self.assertEqual(next_trial["global_order_index"], 2)
        self.assertEqual(next_trial["campaign_seed"], 10001)
        self.assertEqual(next_trial["cell_id"], "A13")

    def test_run_next_contract_is_single_invocation_only(self) -> None:
        self.assertEqual(self.operator.MAX_RUNTIME_INVOCATIONS_PER_CALL, 1)
        self.assertFalse(self.operator.AUTOMATIC_RETRY_ALLOWED)
        self.assertFalse(self.operator.AUTOMATIC_NEXT_ALLOWED)


if __name__ == "__main__":
    unittest.main()
