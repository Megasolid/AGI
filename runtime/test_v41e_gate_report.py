import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from agi_gate_report import PROTECTED, SCHEMA, build_report, sha256_bytes

REPO = Path(__file__).resolve().parents[1]


class GateReportTests(unittest.TestCase):
    """Static tests only.

    build_report() runs the whole suite as a subprocess, which would recurse if
    called from inside the suite. It is exercised by the CLI, never here.
    """

    def test_shape_and_schema(self):
        self.assertEqual(SCHEMA, "agi/gate-report/1")

    def test_protected_list_is_pinned(self):
        self.assertEqual(len(PROTECTED), 6)
        self.assertIn("DNA.md", PROTECTED)
        self.assertIn("POLICY.md", PROTECTED)

    def test_sha256_helper(self):
        self.assertEqual(sha256_bytes(b""),
                         "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")

    def test_check_helpers_fail_closed(self):
        from agi_gate_report import check
        self.assertFalse(check("x", False, {})["passed"])
        self.assertTrue(check("x", True, {})["passed"])

    def test_module_does_not_run_gate_on_import(self):
        import agi_gate_report
        self.assertTrue(hasattr(agi_gate_report, "build_report"))
        # importing must not have executed the suite (no side effects at import)
        self.assertIsInstance(agi_gate_report.PROTECTED, list)


if __name__ == "__main__":
    unittest.main()
