from __future__ import annotations
import unittest
from study6x.runtime.gate_evaluator import GATES, SIGNALS, evaluate_gate
from study6x.audit.reference_gate_evaluator import evaluate_gate_reference

class S6XGateEvaluatorTests(unittest.TestCase):
    def test_full_vector(self):
        e={k:True for k in SIGNALS}
        for gate in GATES:
            self.assertTrue(evaluate_gate(gate,e))
            self.assertTrue(evaluate_gate_reference(gate,e))
    def test_all_unavailability_subsets(self):
        rows=0
        for mask in range(64):
            e={name:not bool(mask & (1<<i)) for i,name in enumerate(SIGNALS)}
            for gate in GATES:
                self.assertEqual(evaluate_gate(gate,e),evaluate_gate_reference(gate,e)); rows+=1
        self.assertEqual(rows,384)
if __name__=="__main__": unittest.main()
