from __future__ import annotations

import ast
import importlib.util
import json
import sys
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
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestWp9CampaignOperatorSidecar(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.operator = _load_operator()

    @staticmethod
    def _position_1_history() -> list[dict[str, object]]:
        return [
            {
                "campaign_seed": 10001,
                "cell_order_index": 1,
                "cell_id": "A19",
                "run_id": "position-1-valid",
                "attempt_status": "VALID",
            }
        ]

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
        self.assertEqual(self.operator.MAX_RUNTIME_INVOCATIONS_PER_CALL, 1)

    def test_operator_never_fetches_or_pulls_live_main(self) -> None:
        source = OPERATOR.read_text(encoding="utf-8")
        self.assertNotIn('"pull"', source)
        self.assertNotIn('"fetch"', source)
        self.assertNotIn("origin/main", source)

    def test_run_one_contains_one_execute_request_and_no_while_loop(self) -> None:
        tree = ast.parse(OPERATOR.read_text(encoding="utf-8"))
        target = next(
            node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "run_one_next_position"
        )
        execute_literals = [
            node
            for node in ast.walk(target)
            if isinstance(node, ast.Constant)
            and node.value == "execute-request"
        ]
        while_nodes = [node for node in ast.walk(target) if isinstance(node, ast.While)]
        self.assertEqual(len(execute_literals), 1)
        self.assertEqual(while_nodes, [])

    def test_position_1_valid_history_resolves_position_2(self) -> None:
        next_trial = self.operator.next_required_trial(
            repo_root=ROOT,
            history=self._position_1_history(),
        )
        self.assertEqual(next_trial["global_order_index"], 2)
        self.assertEqual(next_trial["campaign_seed"], 10001)
        self.assertEqual(next_trial["cell_order_index"], 2)
        self.assertEqual(next_trial["cell_id"], "A13")

    def test_position_2_request_roundtrips_and_composes_without_writes(self) -> None:
        campaign_root = ROOT / "results/wp9/campaign"
        before = sorted(
            str(path.relative_to(ROOT))
            for path in campaign_root.rglob("*")
        ) if campaign_root.exists() else []

        plan, authorization, request = self.operator.prepare_next_request(
            repo_root=ROOT,
            history=self._position_1_history(),
            run_id="operator-test-position-2",
        )

        after = sorted(
            str(path.relative_to(ROOT))
            for path in campaign_root.rglob("*")
        ) if campaign_root.exists() else []

        self.assertEqual(before, after)
        self.assertEqual(plan["campaign_seed"], 10001)
        self.assertEqual(plan["cell_order_index"], 2)
        self.assertEqual(plan["cell_id"], "A13")
        self.assertEqual(plan["factor_context"]["event_id"], "E3")
        self.assertEqual(plan["runtime_family"], "recovery")
        self.assertEqual(plan["runtime_variant"], "e3_command_gateway")
        self.assertTrue(authorization["single_trial_runtime_authorized"])
        self.assertFalse(authorization["campaign_wide_execution_authorized"])
        self.assertEqual(request["global_order_index"], 2)
        self.assertEqual(request["campaign_seed"], 10001)
        self.assertEqual(request["cell_id"], "A13")
        self.assertEqual(request["source_harness"]["event_id"], "E3")
        self.assertFalse(request["automatic_retry_allowed"])
        self.assertFalse(request["automatic_next_case_allowed"])
        self.assertEqual(json.loads(json.dumps(request)), request)

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

    def test_unledgered_source_harness_log_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "run"
            evidence.mkdir(parents=True)
            (evidence / "source-harness.stderr.log").write_text(
                "failed\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                self.operator.classify_unledgered_evidence(evidence)

    def test_atomic_history_append_advances_exactly_one_position(self) -> None:
        history = self._position_1_history()
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
        history = self._position_1_history() + [
            {
                "campaign_seed": 10001,
                "cell_order_index": 2,
                "cell_id": "A13",
                "run_id": "position-2-invalid",
                "attempt_status": "INVALID",
            }
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
