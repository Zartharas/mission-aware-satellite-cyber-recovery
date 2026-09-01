import inspect
import unittest

from study2_security.adjudication import AdjudicationTruth, classify_response
from study2_security.selectors import ObservationSummary, Study2Action, select_action


class AdjudicationTests(unittest.TestCase):
    def test_selector_has_no_adjudication_oracle_parameter(self):
        self.assertNotIn("truth", inspect.signature(select_action).parameters)
        self.assertNotIn("ground_truth", inspect.signature(select_action).parameters)

    def test_permissive_action_with_unauthorized_control_is_unsafe(self):
        result = classify_response(
            Study2Action.PRESERVE_LIMITED_OPERATION,
            AdjudicationTruth(True, False, False),
        )
        self.assertTrue(result.unsafe_permissive)

    def test_restrictive_action_in_known_good_state_is_false_conservative(self):
        result = classify_response(
            Study2Action.HOLD_AND_REQUIRE_EVIDENCE,
            AdjudicationTruth(False, True, True),
        )
        self.assertTrue(result.false_conservative)


if __name__ == "__main__":
    unittest.main()
