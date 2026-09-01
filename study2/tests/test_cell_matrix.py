import unittest

from study2_security.cell_matrix import matrix_sha256, materialize_cell_matrix, target_valid_observations


class CellMatrixTests(unittest.TestCase):
    def test_frozen_membership_identity(self):
        matrix = materialize_cell_matrix()
        self.assertEqual(len(matrix["cells"]), 85)
        self.assertEqual(target_valid_observations(matrix), 3872)
        self.assertEqual(matrix_sha256(matrix), "5087e46f9d416fe5b741fedcb4b1a9d848342087c6e317614dec26a56c2dc081")
        ids = [row["cell_id"] for row in matrix["cells"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_a2_is_represented_only_with_contact_unavailability(self):
        matrix = materialize_cell_matrix()
        a2 = [row for row in matrix["cells"] if row.get("adversary") == "A2"]
        self.assertTrue(a2)
        self.assertTrue(all(row.get("contact") != "K0" for row in a2))


if __name__ == "__main__":
    unittest.main()
