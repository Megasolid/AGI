#!/usr/bin/env python3
"""H0 evidence-consistency checker (revision 10).

Revision 9 shipped a consistency test that was itself vacuous: its regex matched
nothing, the claim dictionary came back empty, zero comparisons ran, and the test
passed. This module exists so a check cannot silently check nothing.

Contract:
  * the parser MUST extract at least one claim, or it raises;
  * every claimed count is compared against the suite's real count;
  * a negative control proves the checker actually fails on a wrong number.

    python h0_evidence.py check <report.md> <runtime-dir>
    python h0_evidence.py self-test <runtime-dir>

Exit 0 = consistent, 1 = inconsistent or vacuous, 2 = usage error.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROW = re.compile(r"^\|\s*`(?P<name>[A-Za-z0-9_]+\.py)`\s*\|\s*(?P<count>\d+)\s*\|", re.M)
TOTAL = re.compile(r"Total H0 contract tests:\s*\*\*(?P<count>\d+)\*\*", re.M)


class EvidenceError(ValueError):
    pass


def real_counts(runtime_dir: Path) -> dict:
    """Actual test counts, measured from the suites themselves."""
    counts = {}
    for path in sorted(runtime_dir.glob("test_h0_contract*.py")):
        n = len(re.findall(r"^\s+def test_", path.read_text(encoding="utf-8"), re.M))
        counts[path.name] = n
    return counts


def parse_claims(report_text: str) -> dict:
    claims = {}
    for m in ROW.finditer(report_text):
        claims[m.group("name")] = int(m.group("count"))
    return claims


def check(report_text: str, runtime_dir: Path, *, allow_subset=False) -> dict:
    claims = parse_claims(report_text)
    if not claims:
        # R10: a check that extracts nothing must not report success
        raise EvidenceError("vacuous check: the report parser extracted zero claims")
    actual = real_counts(runtime_dir)
    mismatches = {}
    for name, claimed in claims.items():
        if name not in actual:
            mismatches[name] = {"claimed": claimed, "actual": None, "reason": "suite not found"}
            continue
        if claimed != actual[name]:
            mismatches[name] = {"claimed": claimed, "actual": actual[name]}
    missing = {}
    if not allow_subset:
        for name, n in actual.items():
            if name not in claims:
                missing[name] = {"actual": n, "reason": "suite not listed in report"}
    total_claim = TOTAL.search(report_text)
    total_ok = None
    if total_claim and not missing:
        total_ok = int(total_claim.group("count")) == sum(actual.values())
    return {"ok": not mismatches and not missing and (total_ok is not False),
            "claims": claims, "actual": actual,
            "mismatches": mismatches, "missing": missing, "total_ok": total_ok}


def self_test(runtime_dir: Path) -> dict:
    """Prove the checker is not vacuous: it must fail on a fabricated report."""
    actual = real_counts(runtime_dir)
    good_lines = "\n".join(f"| `{n}` | {c} | OK |" for n, c in actual.items())
    good = (good_lines + f"\n\nTotal H0 contract tests: **{sum(actual.values())}**\n")
    results = {}

    good_result = check(good, runtime_dir)
    results["accepts_correct_report"] = good_result["ok"]

    # negative control 1: wrong number
    first = sorted(actual)[0]
    bad_lines = "\n".join(f"| `{n}` | {(c + 1) if n == first else c} | OK |"
                          for n, c in actual.items())
    bad = bad_lines + f"\n\nTotal H0 contract tests: **{sum(actual.values())}**\n"
    bad_result = check(bad, runtime_dir)
    results["rejects_wrong_count"] = (not bad_result["ok"]) and first in bad_result["mismatches"]

    # negative control 2: a report with no recognisable table at all
    try:
        check("no table here at all", runtime_dir)
        results["rejects_empty_parse"] = False
    except EvidenceError:
        results["rejects_empty_parse"] = True

    # negative control 3: a suite omitted from the report
    partial = "\n".join(f"| `{n}` | {c} | OK |" for n, c in list(actual.items())[:-1])
    partial_result = check(partial + f"\n\nTotal H0 contract tests: **{sum(actual.values())}**\n", runtime_dir)
    results["rejects_missing_suite"] = (not partial_result["ok"]) and bool(partial_result["missing"])

    # negative control 4: total wrong
    wrong_total = good_lines + "\n\nTotal H0 contract tests: **1**\n"
    results["rejects_wrong_total"] = check(wrong_total, runtime_dir)["total_ok"] is False

    results["all"] = all(v is True for k, v in results.items() if k != "all")
    return results


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="H0 evidence consistency checker")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("report")
    c.add_argument("runtime")
    s = sub.add_parser("self-test")
    s.add_argument("runtime")
    args = ap.parse_args(argv)

    if args.cmd == "check":
        try:
            result = check(Path(args.report).read_text(encoding="utf-8"), Path(args.runtime))
        except EvidenceError as exc:
            print(f"FAIL: {exc}")
            return 1
        print(result)
        return 0 if result["ok"] else 1
    result = self_test(Path(args.runtime))
    print(result)
    return 0 if result["all"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
