import unittest

from study2_security.mutation_assay import run_semantic_mutation_assay


class MutationAssayTests(unittest.TestCase):
    def test_all_frozen_security_mutants_are_killed(self):
        results = run_semantic_mutation_assay()
        self.assertEqual(len(results), 7)
        self.assertEqual(
            {row.mutant for row in results},
            {
                "MUT_ACCEPT_INVALID_SIGNATURE",
                "MUT_ACCEPT_UNTRUSTED_SOURCE",
                "MUT_ACCEPT_STALE",
                "MUT_ACCEPT_WRONG_EPOCH",
                "MUT_ACCEPT_REPLAYED_SEQUENCE",
                "MUT_IGNORE_CONTRADICTION",
                "MUT_IGNORE_RESIDUAL_STATE",
            },
        )
        self.assertTrue(all(row.killed for row in results))


if __name__ == "__main__":
    unittest.main()
