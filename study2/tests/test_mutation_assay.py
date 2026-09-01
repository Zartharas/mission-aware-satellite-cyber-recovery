import unittest

from study2_security.mutation_assay import run_semantic_mutation_assay


class MutationAssayTests(unittest.TestCase):
    def test_all_frozen_security_mutants_are_killed(self):
        results = run_semantic_mutation_assay()
        self.assertEqual(len(results), 5)
        self.assertTrue(all(row.killed for row in results))


if __name__ == "__main__":
    unittest.main()
