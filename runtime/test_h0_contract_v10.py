#!/usr/bin/env python3
"""H0 revision 10 tests — the evidence-consistency check must not be vacuous.

King finding: R9's report-count test used a regex that matched nothing, produced an
empty claim dictionary, compared zero counts, and passed. R10 replaces it with a
checker that:
  R10-1 parses the ACTUAL Markdown table format and extracts claims;
  R10-2 raises when it extracts zero claims (vacuous pass impossible);
  R10-3 compares every listed suite, including v9, and the regression suite;
  R10-4 FAILS on a deliberately wrong count - the negative control R9 lacked.

Run from runtime/: python test_h0_contract_v10.py
"""
import pathlib
import re
import unittest

import h0_evidence
from h0_evidence import EvidenceError, check, parse_claims, real_counts, self_test

RUNTIME = pathlib.Path(__file__).resolve().parent
REPO = RUNTIME.parent


def report_text() -> str:
    return (REPO / "citadel" / "h0" / "H0-CORRECTION-REPORT-R10-20261102.md").read_text(encoding="utf-8")


class R10_1_ParsesTheRealTable(unittest.TestCase):
    def test_parser_extracts_claims_from_the_real_report(self):
        claims = parse_claims(report_text())
        self.assertTrue(claims, "the parser must extract at least one claim")
        self.assertGreaterEqual(len(claims), 9, "every H0 suite should be listed")

    def test_claims_are_integers(self):
        for name, count in parse_claims(report_text()).items():
            self.assertIsInstance(count, int, name)
            self.assertGreater(count, 0, name)


class R10_2_VacuousPassImpossible(unittest.TestCase):
    def test_zero_claims_raises(self):
        with self.assertRaises(EvidenceError) as ctx:
            check("this report has no table whatsoever", RUNTIME)
        self.assertIn("vacuous", str(ctx.exception))

    def test_zero_claims_raises_even_with_some_prose(self):
        text = "## Test evidence\n\nAll suites passed and everything is fine.\n"
        with self.assertRaises(EvidenceError):
            check(text, RUNTIME)


class R10_3_EverySuiteCompared(unittest.TestCase):
    def test_report_matches_reality(self):
        result = check(report_text(), RUNTIME)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["mismatches"], {})
        self.assertEqual(result["missing"], {})

    def test_v9_and_regression_are_covered(self):
        result = check(report_text(), RUNTIME)
        self.assertIn("test_h0_contract_v9.py", result["claims"])
        # the regression suite is measured by the same real_counts helper
        self.assertIn("test_h0_contract_v9.py", result["actual"])

    def test_missing_suite_is_detected(self):
        actual = real_counts(RUNTIME)
        partial = "\n".join(f"| `{n}` | {c} | OK |" for n, c in list(actual.items())[:-1])
        result = check(partial, RUNTIME)
        self.assertFalse(result["ok"])
        self.assertTrue(result["missing"])


class R10_4_NegativeControl(unittest.TestCase):
    def test_wrong_count_fails(self):
        """The check that R9 lacked: it must be observed failing."""
        actual = real_counts(RUNTIME)
        first = sorted(actual)[0]
        lines = "\n".join(f"| `{n}` | {(c + 1) if n == first else c} | OK |"
                          for n, c in actual.items())
        result = check(lines + f"\n\nTotal H0 contract tests: **{sum(actual.values())}**\n", RUNTIME)
        self.assertFalse(result["ok"])
        self.assertIn(first, result["mismatches"])
        self.assertEqual(result["mismatches"][first]["claimed"], actual[first] + 1)

    def test_wrong_total_fails(self):
        actual = real_counts(RUNTIME)
        lines = "\n".join(f"| `{n}` | {c} | OK |" for n, c in actual.items())
        result = check(lines + "\n\nTotal H0 contract tests: **999999**\n", RUNTIME)
        self.assertFalse(result["ok"])

    def test_bundled_self_test_reports_all_controls_pass(self):
        result = self_test(RUNTIME)
        self.assertTrue(result["all"], result)
        for key in ("accepts_correct_report", "rejects_wrong_count",
                    "rejects_empty_parse", "rejects_missing_suite", "rejects_wrong_total"):
            self.assertIs(result[key], True, key)


if __name__ == "__main__":
    unittest.main()
