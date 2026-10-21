from __future__ import annotations

import unittest

from study6x.validation.validate_local_cfs_pin import extract_unique_region


class ValidateLocalCfsPinTests(unittest.TestCase):
    def test_signed_region_isolated_from_unsigned_duplicate_expression(self) -> None:
        source = """
uint8 LC_SignedCompare(uint16 WatchIndex, int32 WPValue, int32 CompareValue)
{
    EvalResult = (WPValue > CompareValue) ? LC_WATCH_TRUE : LC_WATCH_FALSE;
    EvalResult = (WPValue >= CompareValue) ? LC_WATCH_TRUE : LC_WATCH_FALSE;
}

uint8 LC_UnsignedCompare(uint16 WatchIndex, uint32 WPValue, uint32 CompareValue)
{
    EvalResult = (WPValue > CompareValue) ? LC_WATCH_TRUE : LC_WATCH_FALSE;
    EvalResult = (WPValue >= CompareValue) ? LC_WATCH_TRUE : LC_WATCH_FALSE;
}
"""
        region = extract_unique_region(
            source,
            "uint8 LC_SignedCompare(",
            "uint8 LC_UnsignedCompare(",
        )
        self.assertEqual(
            region.count(
                "EvalResult = (WPValue > CompareValue) ? "
                "LC_WATCH_TRUE : LC_WATCH_FALSE;"
            ),
            1,
        )
        self.assertEqual(
            region.count(
                "EvalResult = (WPValue >= CompareValue) ? "
                "LC_WATCH_TRUE : LC_WATCH_FALSE;"
            ),
            1,
        )

    def test_duplicate_start_marker_fails_closed(self) -> None:
        with self.assertRaises(SystemExit):
            extract_unique_region(
                "uint8 LC_SignedCompare(\nuint8 LC_SignedCompare(\n"
                "uint8 LC_UnsignedCompare(",
                "uint8 LC_SignedCompare(",
                "uint8 LC_UnsignedCompare(",
            )


if __name__ == "__main__":
    unittest.main()
