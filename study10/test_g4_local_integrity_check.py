"""Synthetic fixtures only. No ESA, OPS-SAT or Hack-A-Sat source bytes."""
from __future__ import annotations
import hashlib
import io
from pathlib import Path
import tempfile
import unittest
import zipfile

import g4_local_integrity_check as audit


def mkzip(entries: dict[str, bytes]) -> bytes:
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w', compression=zipfile.ZIP_STORED, allowZip64=True) as z:
        for name, data in entries.items():
            z.writestr(name, data)
    return b.getvalue()


def expected_for_file(p: Path, n: int, total: int) -> dict:
    b = p.read_bytes()
    return dict(id='ESA_M1_v2', family='ESA_ADB', basename=p.name, path=p,
                md5=hashlib.md5(b, usedforsecurity=False).hexdigest(),
                sha256=hashlib.sha256(b).hexdigest(), expected_size=len(b),
                zip_directory_count=n, zip_uncompressed_bytes=total)


class SyntheticIntegrityTests(unittest.TestCase):
    def test_safe_zip_names(self):
        for v in ('../escape', '/etc/passwd', 'C:/temp/file', 'dir\\file',
                  'a/../../b', '', '\\relative'):
            self.assertFalse(audit.safe_member_name(v), v)
        for v in ('a/b.csv', 'ESA-Mission1/channels/channel_2.zip'):
            self.assertTrue(audit.safe_member_name(v))

    def test_full_nested_pass_and_outer_only_incomplete(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            inner_bytes = mkzip({'rows.csv': b'synthetic test bytes\n' * 9})
            original = root/'ESA-Mission1 (1).zip'
            original.write_bytes(mkzip({'m/channels/channel_1.zip': inner_bytes,
                                        'm/channels.csv': b'synthetic,column\n'}))
            expected = expected_for_file(original, 2, len(inner_bytes)+len(b'synthetic,column\n'))
            full = audit.audit_one(expected, outer_only=False, scratch=root, limits=audit.DEFAULT_LIMITS)
            self.assertEqual(full['status'], 'PASS_FULL_OUTER_AND_NESTED_CRC', full)
            self.assertEqual(full['archive_check']['nested_archives'], 1)
            self.assertEqual(full['archive_check']['nested_crc'], 'PASS')
            outer = audit.audit_one(expected, outer_only=True, scratch=None, limits=audit.DEFAULT_LIMITS)
            self.assertEqual(outer['status'], 'INCOMPLETE_NESTED_NOT_CHECKED')
            self.assertEqual(outer['archive_check']['outer_crc'], 'PASS')

    def test_inner_corruption_rejected_without_writing_contents(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            inner=bytearray(mkzip({'test.csv': b'UNIQUE_TEST_SENTINEL_123'}))
            index=inner.find(b'UNIQUE_TEST_SENTINEL_123')
            self.assertGreaterEqual(index, 0)
            inner[index]^=1  # file's internal CRC no longer agrees with payload
            p=root/'ESA-Mission1.zip'
            p.write_bytes(mkzip({'nested.zip': bytes(inner)}))
            expected=expected_for_file(p, 1, len(inner))
            got=audit.audit_one(expected, outer_only=False, scratch=root, limits=audit.DEFAULT_LIMITS)
            self.assertEqual(got['status'], 'FAIL_INTEGRITY_OR_RESOURCE_LIMIT', got)
            self.assertEqual(got['failure_code'], 'BadZipFile')

    def test_bad_filename_member_and_missing(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            p=root/'ESA-Mission1.zip'
            p.write_bytes(mkzip({'../evil': b'not touched'}))
            e=expected_for_file(p, 1, len(b'not touched'))
            bad=audit.audit_one(e, outer_only=False, scratch=root, limits=audit.DEFAULT_LIMITS)
            self.assertEqual(bad['failure_code'], 'ZIP_UNSAFE_MEMBER_PATH')
            p.unlink()
            missing=audit.audit_one(e, outer_only=False, scratch=root, limits=audit.DEFAULT_LIMITS)
            self.assertEqual(missing['status'], 'MISSING_LOCAL_FILE')

    def test_md5_sha_and_resource_mismatch_are_fail_closed(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            p=root/'ESA-Mission1.zip'
            nested=mkzip({'nested.txt':b'abc'})
            p.write_bytes(mkzip({'inner.zip':nested}))
            e=expected_for_file(p, 1, len(nested))
            e['sha256']='0'*64
            result=audit.audit_one(e, outer_only=False, scratch=root, limits=audit.DEFAULT_LIMITS)
            self.assertEqual(result['failure_code'], 'SOURCE_HASH_OR_SIZE_MISMATCH')
            e=expected_for_file(p, 1, len(nested))
            limits=dict(audit.DEFAULT_LIMITS, max_nested_zip_stage=1)
            result=audit.audit_one(e, outer_only=False, scratch=root, limits=limits)
            self.assertEqual(result['failure_code'], 'NESTED_ZIP_TEMP_STAGE_LIMIT')

    def test_zip_file_symlink_blocked(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            actual=root/'actual.txt'
            actual.write_text('TEST\n')
            linked=root/'ESA-Mission1.zip'
            linked.symlink_to(actual)
            e={'id':'ESA_M1_v1','family':'ESA_ADB', 'basename':linked.name,
               'path':linked,'md5':'0'*32,'sha256':'0'*64}
            got=audit.audit_one(e, outer_only=True, scratch=None, limits=audit.DEFAULT_LIMITS)
            self.assertEqual(got['status'], 'FAIL_BAD_PATH_OR_SYMLINK')

if __name__ == '__main__':
    unittest.main()
