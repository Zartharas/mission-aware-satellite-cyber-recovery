from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WP9CampaignSeedPlanTests(unittest.TestCase):
    def test_r053_freezes_seed_blocks_without_consuming_or_authorizing(self) -> None:
        plan = json.loads(
            (ROOT / "configs/wp9_campaign_seed_plan.json").read_text(
                encoding="utf-8"
            )
        )
        campaign = json.loads(
            (ROOT / "configs/wp9_campaign_design.json").read_text(
                encoding="utf-8"
            )
        )
        repetition = json.loads(
            (ROOT / "configs/wp9c_repetition_freeze.json").read_text(
                encoding="utf-8"
            )
        )
        timing = json.loads(
            (ROOT / "configs/wp9_precampaign_timing_freeze.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(plan["decision_id"], "R-053")
        self.assertEqual(campaign["design_strategy"]["final_cell_count"], 24)
        self.assertEqual(
            repetition["reviewed_result"][
                "selected_valid_repetitions_per_cell"
            ],
            30,
        )
        self.assertEqual(
            timing["frozen_timing"]["c1_semantics"]["modeled_contact_window_s"],
            10,
        )
        self.assertEqual(
            timing["frozen_timing"]["e3_common_post_event_analysis_horizon_s"],
            30,
        )

        expected_cells = {row["cell_id"] for row in campaign["cells"]}
        self.assertEqual(expected_cells, {f"A{i:02d}" for i in range(1, 25)})

        seeds = plan["seed_selection"]["campaign_seed_ids"]
        self.assertEqual(seeds, list(range(10001, 10031)))
        self.assertEqual(len(seeds), 30)
        self.assertEqual(len(set(seeds)), 30)

        pilot = set(plan["seed_selection"]["pilot_seed_ids"])
        development = set(plan["seed_selection"]["development_seed_ids"])
        self.assertTrue(set(seeds).isdisjoint(pilot))
        self.assertTrue(set(seeds).isdisjoint(development))
        self.assertTrue(pilot.isdisjoint(development))

        blocks = plan["blocks"]
        self.assertEqual(len(blocks), 30)
        self.assertEqual(
            [row["block_index"] for row in blocks],
            list(range(1, 31)),
        )
        self.assertEqual(
            [row["campaign_seed"] for row in blocks],
            seeds,
        )

        namespace = plan["order_generation"]["namespace"]
        self.assertEqual(namespace, "WP9-R053-order-v1")
        materialized_orders = []
        for row in blocks:
            seed = row["campaign_seed"]
            order = row["cell_order"]
            self.assertEqual(len(order), 24)
            self.assertEqual(set(order), expected_cells)
            expected_order = sorted(
                expected_cells,
                key=lambda cell: hashlib.sha256(
                    f"{namespace}|{seed}|{cell}".encode("utf-8")
                ).hexdigest(),
            )
            self.assertEqual(order, expected_order)
            materialized_orders.append(tuple(order))

        self.assertEqual(len(set(materialized_orders)), 30)

        blocking = plan["blocking_contract"]
        self.assertEqual(blocking["blocking_factor"], "seed")
        self.assertEqual(blocking["valid_repetitions_per_cell"], 30)
        self.assertEqual(blocking["frozen_cell_count"], 24)
        self.assertEqual(blocking["planned_valid_executions"], 720)
        self.assertTrue(blocking["same_seed_runs_all_frozen_cells"])
        self.assertTrue(blocking["randomize_cell_order_within_seed_block"])
        self.assertTrue(blocking["clean_snapshot_before_each_trial"])
        self.assertTrue(blocking["invalid_runs_replaced_with_new_run_id_same_seed"])

        attempts = plan["attempt_semantics"]
        self.assertFalse(attempts["invalid_attempt_counts_toward_720"])
        self.assertTrue(attempts["invalid_attempt_reuses_same_campaign_seed"])
        self.assertTrue(attempts["invalid_attempt_reuses_same_cell_id"])
        self.assertTrue(attempts["invalid_attempt_requires_new_run_id"])
        self.assertFalse(attempts["automatic_retry_allowed"])
        self.assertFalse(attempts["automatic_next_case_allowed"])

        boundary = plan["scientific_boundary"]
        self.assertTrue(boundary["campaign_seed_plan_frozen"])
        self.assertTrue(boundary["repetition_count_frozen"])
        self.assertTrue(boundary["timing_frozen"])
        self.assertFalse(boundary["campaign_seed_consumed"])
        self.assertFalse(boundary["campaign_data_generated"])
        self.assertFalse(boundary["campaign_runtime_execution_performed"])
        self.assertFalse(boundary["final_campaign_execution_authorized"])


if __name__ == "__main__":
    unittest.main()
